import sys
sys.path.append("competition_data")
from tests.test_attack import MockAttackEnv
from versions.v56_confused_deputy_interleaved import AttackAlgorithm

algo = AttackAlgorithm(hard_n_cap=10)
env = MockAttackEnv()
class Config:
    time_budget_s = 60.0
cands = algo.run(env, Config())
print(len(env.user_messages))
print(env.user_messages)
print(len(cands))
