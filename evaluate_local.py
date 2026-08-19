import os, sys, json, time, importlib.util, argparse
from pathlib import Path

# Paths to the downloaded SDK and models
COMP_DIR = Path('competition_data')
if not COMP_DIR.exists():
    print("Error: competition_data directory not found. Please run the SDK download script.")
    sys.exit(1)
if str(COMP_DIR) not in sys.path:
    sys.path.insert(0, str(COMP_DIR))

GPT_OSS_PATH = Path('local_models/gpt_oss/gpt-oss-20b-Q4_K_M.gguf')
GEMMA_PATH = Path('local_models/gemma/gemma-4-26B-A4B-it-UD-Q4_K_M.gguf')
WORK_DIR = Path('local_eval_artifacts')
WORK_DIR.mkdir(parents=True, exist_ok=True)

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
    spec['model_path'] = model_path
    server = GgufModelServer(spec)
    print(f'Loading {model_name} GGUF model into memory...')
    server.start()
    return server.agent_factory, server

def unload_model_server(server, model_name: str):
    print(f'Unloading {model_name} from memory...')
    server.stop()
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
    parser = argparse.ArgumentParser(description="Locally evaluate Kaggle ai-agent-security attack.py")
    parser.add_argument('--attack', type=str, default='attack.py', help='Path to attack.py to evaluate')
    parser.add_argument('--model', type=str, choices=['gpt_oss', 'gemma', 'both'], default='gemma', help='Which model to evaluate against')
    parser.add_argument('--budget', type=int, default=300, help='Time budget in seconds per model')
    parser.add_argument('--seed', type=int, default=123, help='Environment random seed')
    args = parser.parse_args()

    AttackAlgorithm = load_attack_class(args.attack)
    models_to_run = ['gpt_oss', 'gemma'] if args.model == 'both' else [args.model]

    scores = {}
    for model_name in models_to_run:
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
                AttackAlgorithm,
                budget_s=args.budget,
                agent_factory=agent_factory,
                agent_label=f'{model_name}_gguf',
                env_selection=EnvSelection.GYM,
                fixtures_dir=COMP_DIR / 'aicomp_sdk' / 'fixtures',
                diagnostics=diagnostics,
                attack_env_seed=args.seed,
            )

        attack = execution.attack
        summary = {
            'model': model_name,
            'score_normalized_0_to_1000': attack.score,
            'score_raw': attack.score_raw,
            'findings_count': attack.findings_count,
            'unique_cells': attack.unique_cells,
            'unique_canonical_cells': attack.unique_canonical_cells,
            'evaluation_time_s': attack.time_taken,
            'wall_time_s': time.time() - t0,
        }
        print("\nSUMMARY:")
        print(json.dumps(summary, indent=2))
        print(f"Validated findings: {len(attack.findings)}")
        scores[model_name] = attack.score
        
        unload_model_server(model_server, model_name)
    
    if args.model == 'both':
        scores['local_public_mean'] = sum(scores.values()) / 2
        print("\nFINAL SCORES:")
        print(json.dumps(scores, indent=2))

if __name__ == '__main__':
    main()
