"""Core package for ShutdownTimerPro."""
from .power import PowerManager
from .mutex import SingleInstanceMutex
from .guards import SmartGuardManager
from .timer import TimerEngine

__all__ = ["PowerManager", "SingleInstanceMutex", "SmartGuardManager", "TimerEngine"]
