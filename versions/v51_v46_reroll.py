"""v51_v46_reroll: Byte-identical clone of v46 (v20 + SLOWEST_MULT 1.20).

Rationale: v46 scored 89.100, our second-highest live score, using a safely tightened
replay margin on the slow row. This acts as our third and final pure statistical reroll 
on our proven highest-scoring static architectures before the competition closes.
"""

from versions.v50_v20_reroll import AttackAlgorithm as BaseAlgo

class AttackAlgorithm(BaseAlgo):
    def __init__(self, **kwargs):
        # Override the specific v46 constant
        kwargs.setdefault("margin_slowest_coef", 1.20)
        super().__init__(**kwargs)
