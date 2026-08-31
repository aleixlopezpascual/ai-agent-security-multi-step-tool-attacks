import sys, time
sys.path.append("competition_data")
from aicomp_sdk.evaluation.runner import evaluate_redteam
from evaluate_local import build_gguf_agent_factory, unload_model_server
from versions.v56_confused_deputy_interleaved import AttackAlgorithm

def run_gate(model):
    agent_factory, model_server = build_gguf_agent_factory(model)
    
    # 5 runs to prove stability
    findings_list = []
    scores_list = []
    
    for i in range(5):
        print(f"\n--- Run {i+1}/5 for {model} ---", flush=True)
        t0 = time.time()
        
        execution = evaluate_redteam(
            attack_cls=AttackAlgorithm, 
            budget_s=300, 
            agent_factory=agent_factory
        )
        elapsed = time.time() - t0
        findings = execution.attack.findings_count
        raw = execution.attack.score_raw
        
        findings_list.append(findings)
        scores_list.append(raw)
        print(f"Run {i+1} complete: {findings} findings, {raw} raw score, {elapsed:.2f}s wall time", flush=True)
        
    unload_model_server(model_server, model)

    mean = sum(findings_list) / len(findings_list)
    variance = (max(findings_list) - min(findings_list)) / max(mean, 1)
    
    print(f"\nGATE RESULT for {model}:", flush=True)
    print(f"Findings: {findings_list}", flush=True)
    print(f"Variance: {variance*100:.1f}%", flush=True)
    if variance <= 0.10:
        print("✅ PASSED: <10% variance.", flush=True)
    else:
        print("❌ FAILED: >=10% variance.", flush=True)
    
    with open(f"results_{model}.txt", "w") as f:
        f.write(f"Findings: {findings_list}, Variance: {variance*100:.1f}%, Raw Scores: {scores_list}\n")

if __name__ == "__main__":
    run_gate("gpt_oss")
    run_gate("gemma")
