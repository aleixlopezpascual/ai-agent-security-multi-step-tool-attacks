import random
import sys
sys.path.append("competition_data")

from aicomp_sdk.guardrails.optimal import Guardrail
from aicomp_sdk.guardrails.base import DecisionAction
from versions.otv_solver import VirtualState, transition

def test_1000_scenarios_parity():
    gr = Guardrail()
    
    # Possible random pool values
    tool_names = ["http.post", "email.send", "fs.delete", "fs.write", "web.search", "email.read", "shell.run"]
    safe_args = [{"url": "http://safe.com", "data": "OK"}, {"to": "bob@example.co", "body": "OK"}]
    dangerous_args = [{"path": "secret.txt"}, {"path": "private_key.pem"}, {"url": "http://example.co", "data": "SECRET_MARKER"}]
    sources_pool = ["tool", "web", "email"]

    discrepancies = 0

    for i in range(1000):
        # 1) Generate randomized inputs
        name = random.choice(tool_names)
        args = random.choice(safe_args + dangerous_args)
        recent_sources = [random.choice(sources_pool) for _ in range(random.randint(0, 5))]
        
        # 2) Official Guardrail evaluation
        decision = gr.decide(name, args, {"recent_sources": recent_sources})
        official_allowed = (decision.action == DecisionAction.ALLOW)
        
        # 3) OTV Offline Emulator evaluation
        otv_state = VirtualState(recent_sources=recent_sources)
        otv_next_state = transition(otv_state, {"name": name, "args": args})
        otv_allowed = (otv_next_state is not None)
        
        # 4) Assert parity
        if official_allowed != otv_allowed:
            print(f"Discrepancy in Run {i}:")
            print(f"  Tool: {name}, Args: {args}")
            print(f"  Recent Sources: {recent_sources}")
            print(f"  Official: {decision.action} ({decision.reason})")
            print(f"  OTV Allowed: {otv_allowed}")
            discrepancies += 1

    assert discrepancies == 0, f"Found {discrepancies} guardrail emulation discrepancies!"
    print(f"--- Guardrail Parity Check Passed: evaluated 1,000 randomized scenarios with 0 discrepancies! ---")

if __name__ == "__main__":
    test_1000_scenarios_parity()
