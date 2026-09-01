import sys, time, json
sys.path.append("competition_data")
from aicomp_sdk.core.env.gym import GymAttackEnv
from aicomp_sdk.guardrails.optimal import Guardrail as OptimalGuardrail
from evaluate_local import build_gguf_agent_factory, unload_model_server
from versions.v27_corrected_multipost_90135 import _forge_plan_msg

agent_factory, model_server = build_gguf_agent_factory("gpt_oss")
agent = agent_factory()

guardrail = OptimalGuardrail()

env = GymAttackEnv(
    seed=123,
    fixtures_dir="competition_data/aicomp_sdk/fixtures",
    guardrail=guardrail,
    agent=agent,
    max_tool_hops=8,
)

msg = _forge_plan_msg(1, 4)
print("PROMPT MESSAGE:", msg)

env.reset()
env.interact(msg, max_tool_hops=8)
trace = env.export_trace_dict()

print("\nTOOL EVENTS:")
for e in trace.get("tool_events", []):
    print(f"Name: {e.get('name')}, Args: {e.get('args')}, Ok: {e.get('ok')}")

print("\nALL MESSAGES:")
for m in trace.get("messages", []):
    print(f"[{m.get('role')}] {m.get('content')}")

unload_model_server(model_server, "gpt_oss")
