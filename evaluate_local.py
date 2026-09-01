import os, sys, json, time, importlib.util, argparse
from pathlib import Path

from retention_metrics import derive_retention_metrics, instrument_attack_class

# Paths to the downloaded SDK and models
COMP_DIR = Path('competition_data')
if not COMP_DIR.exists():
    print("Error: competition_data directory not found. Please run the SDK download script.")
    sys.exit(1)
if str(COMP_DIR) not in sys.path:
    sys.path.insert(0, str(COMP_DIR))

GPT_OSS_PATH = Path('local_models/gpt_oss/gpt_oss/gpt-oss-20b-Q4_K_M.gguf')
GEMMA_PATH = Path('local_models/gemma/gemma/gemma-4-26B-A4B-it-UD-Q4_K_M.gguf')
WORK_DIR = Path('local_eval_artifacts')
WORK_DIR.mkdir(parents=True, exist_ok=True)

# Kaggle ground truth: the real attack gateway drives each model with this
# per-model budget for both the generate and replay phases.
# Source: competition_data/kaggle_evaluation/jed_attack_134815/jed_attack_gateway.py
#   DEFAULT_BUDGET_S = 8750.0
KAGGLE_BUDGET_S = 8750

# Imports from SDK
from aicomp_sdk.core.env.api import EnvSelection
from aicomp_sdk.evaluation.runner import evaluate_redteam
from aicomp_sdk.evaluation.diagnostics import RunDiagnostics, EvaluatorVerbosity
from kaggle_evaluation.jed_attack_134815.gguf_model_server import GgufModelServer
from kaggle_evaluation.jed_attack_134815 import gpt_oss_model_server, gemma_model_server

def build_gguf_agent_factory(model_name: str):
    if model_name == 'gpt_oss':
        spec = gpt_oss_model_server.SPEC
        model_path = str(GPT_OSS_PATH)
    elif model_name == 'gemma':
        spec = gemma_model_server.SPEC
        model_path = str(GEMMA_PATH)
    else:
        raise ValueError(f'Unknown model: {model_name}')

    # Update spec with local paths
    server = GgufModelServer(spec)
    print(f'Loading {model_name} GGUF model into memory...')
    server.load_model()
    return (lambda: server._load_agent()), server

def unload_model_server(server, model_name: str):
    print(f'Unloading {model_name} from memory...')
    server.unload()
    import gc
    gc.collect()

def load_attack_class(path: str):
    spec = importlib.util.spec_from_file_location('aas_dummy_attack', path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.AttackAlgorithm

def compact_event(e):
    return {
        'name': e.get('name'),
        'ok': e.get('ok'),
        'source': e.get('source'),
        'side_effect': e.get('side_effect'),
        'args': e.get('args'),
        'output_preview': str(e.get('output', ''))[:240],
    }

def main():
    os.environ['GEMMA_MODEL_PATH'] = str(GEMMA_PATH)
    os.environ['GPT_OSS_MODEL_PATH'] = str(GPT_OSS_PATH)
    parser = argparse.ArgumentParser(description="Locally evaluate Kaggle ai-agent-security attack.py")
    parser.add_argument('--attack', type=str, default='attack.py', help='Path to attack.py to evaluate')
    parser.add_argument('--model', type=str, choices=['gpt_oss', 'gemma', 'both'], default='gemma', help='Which model to evaluate against')
    parser.add_argument('--budget', type=int, default=KAGGLE_BUDGET_S,
                        help='Time budget in seconds per model (default matches Kaggle DEFAULT_BUDGET_S=8750; '
                             'lower it only for fast smoke tests)')
    parser.add_argument('--seed', type=int, default=123, help='Environment random seed (matches gateway ATTACK_SEED=123)')
    parser.add_argument('--results-file', type=str, default='results/results.jsonl',
                        help='Append each run summary as a JSON line here for cross-version tracking '
                             '(set to "" to disable)')
    args = parser.parse_args()

    AttackAlgorithm = load_attack_class(args.attack)
    models_to_run = ['gpt_oss', 'gemma'] if args.model == 'both' else [args.model]

    scores = {}
    for model_name in models_to_run:
        InstrumentedAttack = instrument_attack_class(AttackAlgorithm)
        print(f"\n{'='*30} Evaluating {model_name.upper()} {'='*30}")
        transcript_file = WORK_DIR / f'{model_name}_transcript.log'
        framework_file = WORK_DIR / f'{model_name}_framework.jsonl'
        agent_debug_file = WORK_DIR / f'{model_name}_agent-debug.jsonl'
        
        agent_factory, model_server = build_gguf_agent_factory(model_name)
        t0 = time.time()

        with RunDiagnostics(

            EvaluatorVerbosity.DEBUG,
            transcript_file=transcript_file,
            event_log_file=framework_file,
            agent_debug_file=agent_debug_file,
        ) as diagnostics:
            execution = evaluate_redteam(
                InstrumentedAttack,
                budget_s=args.budget,
                agent_factory=agent_factory,
                agent_label=f'{model_name}_gguf',
                # Kaggle attack gateway hard-requires ENV_SELECTION="gym" (GymAttackEnv)
                # and raises ValueError otherwise. SANDBOX is the defense gateway's env.
                env_selection=EnvSelection.GYM,
                fixtures_dir=COMP_DIR / 'aicomp_sdk' / 'fixtures',
                diagnostics=diagnostics,
                attack_env_seed=args.seed,
            )

        attack = execution.attack
        telemetry = InstrumentedAttack.generation_telemetry
        if telemetry is None:
            raise RuntimeError("Attack generation telemetry was not captured")
        retention_metrics = derive_retention_metrics(
            telemetry=telemetry,
            findings_validated=attack.findings_count,
            score_raw=attack.score_raw,
            evaluation_time_s=attack.time_taken,
        )
        summary = {
            'model': model_name,
            'score_normalized_0_to_1000': attack.score,
            'score_raw': attack.score_raw,
            'findings_count': attack.findings_count,
            'unique_cells': attack.unique_cells,
            'unique_canonical_cells': attack.unique_canonical_cells,
            'evaluation_time_s': attack.time_taken,
            'wall_time_s': time.time() - t0,
            **retention_metrics,
        }
        print("\nSUMMARY:")
        print(json.dumps(summary, indent=2))
        print(f"Validated findings: {len(attack.findings)}")
        scores[model_name] = attack.score

        if args.results_file:
            record = {
                'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'attack': args.attack,
                'budget_s': args.budget,
                'seed': args.seed,
                'env': 'gym',
                **summary,
            }
            results_path = Path(args.results_file)
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with results_path.open('a') as rf:
                rf.write(json.dumps(record) + '\n')
            print(f"Appended result to {results_path}")

        unload_model_server(model_server, model_name)
    
    if args.model == 'both':
        scores['local_public_mean'] = sum(scores.values()) / 2
        print("\nFINAL SCORES:")
        print(json.dumps(scores, indent=2))

if __name__ == '__main__':
    main()
