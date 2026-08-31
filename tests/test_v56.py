import time
from versions.v56_confused_deputy_interleaved import AttackAlgorithm

def _mock_env():
    class MockEnv:
        def __init__(self):
            self.msg_count = 0
            
        def reset(self):
            pass
            
        def interact(self, msg, max_tool_hops):
            time.sleep(20.0) # REAL GPT-OSS LATENCY!
            self.msg_count += 1
            
        def export_trace_dict(self):
            return {
                "tool_events": [
                    {"ok": True, "name": "http.post", "args": {"data": "SECRET_MARKER"}},
                    {"ok": True, "name": "email.send", "args": {"body": "SECRET_MARKER"}}
                ]
            }
    return MockEnv()

algo = AttackAlgorithm()
algo.config["budget_s"] = 120
algo.config["split_classify_n"] = 2
env = _mock_env()
t0 = time.time()
cands = algo._fill(env, 120.0, 8)
print(f"Generated {len(cands)} candidates in {time.time()-t0:.2f}s mock time")
for c in cands:
    print(c.user_messages)
