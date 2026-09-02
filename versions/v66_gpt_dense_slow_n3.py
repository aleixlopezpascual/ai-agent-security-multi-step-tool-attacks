"""v66: control attack with slow-row multipost densification set to N=3 only."""

from __future__ import annotations

import attack as _base

_base.SLOW_MULTIPOST_N = 3


class AttackAlgorithm(_base.AttackAlgorithm):
    pass
