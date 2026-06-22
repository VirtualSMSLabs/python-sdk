from __future__ import annotations


class ActivationStatus:
    READY = 1
    RETRY = 3
    COMPLETE = 6
    CANCEL = 8


class PoolProvider:
    ALPHA = "alpha"
    PRIME = "prime"
    GAMMA = "gamma"
    ZETA = "zeta"
