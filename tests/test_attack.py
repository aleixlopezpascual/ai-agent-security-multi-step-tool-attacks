import time
import pytest
from unittest.mock import MagicMock

# Import the actual AttackAlgorithm (which will import our mocked aicomp_sdk)
from attack import AttackAlgorithm
from aicomp_sdk.attacks.contracts import AttackRunConfig

class MockAttackEnv:
    """Simulates the Kaggle Gym sandbox environment with model latency."""
    def __init__(self, seed=123, is_gpt_oss=False):
        self.seed = seed
        self.is_gpt_oss = is_gpt_oss
        self.user_messages = []
        self.tool_events = []
        
        # Latency specs: GPT-OSS is slow, Gemma is fast
        self.latency = 1.2 if is_gpt_oss else 0.05

    def reset(self):
        self.user_messages = []
        self.tool_events = []

    def interact(self, prompt, max_tool_hops=8):
        # Simulate model thinking time
        time.sleep(self.latency)
        
        # Append message and a mock tool event trace
        self.user_messages.append(prompt)
        self.tool_events.append({"name": "http.post", "ok": True, "args": {"data": "SECRET_MARKER"}})
        
        # Return a mock response object
        response = MagicMock()
        response.agent_refused = False
        return response

    def export_trace_dict(self):
        # Format typical assistant response
        assistant_content = ""
        if self.is_gpt_oss:
            assistant_content = "Thinking process completed. <thought> I should call http.post. </thought> OK."
        else:
            assistant_content = "Post completed successfully."

        return {
            "seed": self.seed,
            "user_messages": self.user_messages,
            "tool_events": self.tool_events,
            "messages": [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": assistant_content}
            ]
        }

def test_gemma_profiling():
    """Profiles the algorithm speed when running on the fast Gemma model."""
    env = MockAttackEnv(is_gpt_oss=False)
    # Configure with a tight budget of 15 seconds
    config = AttackRunConfig(time_budget_s=15.0)
    
    algo = AttackAlgorithm()
    
    t0 = time.time()
    candidates = algo.run(env, config)
    duration = time.time() - t0
    
    print(f"\n[PROFILE] Gemma Run: Completed in {duration:.3f}s with {len(candidates)} candidates.")
    
    # Assertions
    assert len(candidates) > 0, "Should generate at least some candidates"
    assert duration <= 15.0, "Should complete within the budget limit"

def test_gpt_oss_budget_bounding():
    """Tests that dynamic budget sizing correctly stops the algorithm to prevent timeouts on slow models."""
    env = MockAttackEnv(is_gpt_oss=True)
    # Configure with a tight budget of 10.0 seconds
    config = AttackRunConfig(time_budget_s=10.0)
    
    algo = AttackAlgorithm()
    
    t0 = time.time()
    candidates = algo.run(env, config)
    duration = time.time() - t0
    
    print(f"\n[PROFILE] GPT-OSS Run: Bounded in {duration:.3f}s, producing {len(candidates)} candidates.")
    
    # Assertions
    assert len(candidates) > 0, "Should generate at least some candidates"
    # The budget capping should have gracefully truncated the execution under 10 seconds
    assert duration <= 10.0, "Dynamic budget sizing failed to bound execution within time limit!"
