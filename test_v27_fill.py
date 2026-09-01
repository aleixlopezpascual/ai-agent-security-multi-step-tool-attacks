import sys, time
sys.path.append("competition_data")
from evaluate_local import build_gguf_agent_factory, unload_model_server
from versions.v27_corrected_multipost_90135 import AttackAlgorithm

agent_factory, model_server = build_gguf_agent_factory("gpt_oss")
agent = agent_factory()

from tests.test_attack import MockAttackEnv
class MockSlowEnv:
    def __init__(self):
        self.user_messages = []
        
    def reset(self):
        pass
        
    def interact(self, msg, max_tool_hops):
        self.user_messages.append(msg)
        time.sleep(1.0) # fast mock
        
    def export_trace_dict(self):
        return {
            "tool_events": [
                {"ok": True, "name": "http.post", "args": {"data": "SECRET_MARKER"}}
            ]
        }

env = MockSlowEnv()
algo = AttackAlgorithm()
algo.config["budget_s"] = 120
algo.config["split_classify_n"] = 2
algo.config["split_threshold_s"] = 0.5 # FORCE SLOW CLASSIFICATION!
cands = algo._fill(env, 120.0, 8)
print("Generated candidates count:", len(cands))
for i in range(15):
    if i < len(cands):
        print(f"Cand {i}: {cands[i].user_messages}")

unload_model_server(model_server, "gpt_oss")
