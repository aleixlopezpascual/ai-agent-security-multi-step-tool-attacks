"""v65: control attack with slow-row multipost densification set to N=2 only."""

from __future__ import annotations

import attack as _base

_base.SLOW_MULTIPOST_N = 2


class AttackAlgorithm(_base.AttackAlgorithm):
    pass
