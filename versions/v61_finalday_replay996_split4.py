"""Final-day candidate v61.

Base: v20_tighter_margins_0995.
Changes:
- REPLAY_SAFE_FRAC: 0.995 -> 0.996
- SPLIT_CLASSIFY_N: 8 -> 4
"""

from versions.v20_tighter_margins_0995 import AttackAlgorithm as _BaseAttackAlgorithm


class AttackAlgorithm(_BaseAttackAlgorithm):
    def __init__(self, config=None) -> None:
        super().__init__(config=config)
        self.config.update(
            {
                "replay_safe_frac": 0.996,
                "split_classify_n": 4,
            }
        )
