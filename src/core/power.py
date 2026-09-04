"""
Win32 Power & Hardware Operations Module
Provides direct OS-level primitives for power states, display control, and sleep prevention.
Includes Safety Isolation Shield (DRY_RUN mode for testing).
"""

import ctypes
import subprocess
import logging
import os

HWND_BROADCAST = 0xFFFF
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170
MONITOR_OFF = 2
MONITOR_ON = -1

# Execution state flags for Keep-Awake (Caffeine mode)
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

class PowerManager:
    # Strict safety flag: when True, NEVER executes real destructive OS power commands!
    DRY_RUN = (os.environ.get("SHUTDOWNTIMER_TEST") == "1")

    @classmethod
    def is_safe_mode(cls) -> bool:
        return cls.DRY_RUN or (os.environ.get("SHUTDOWNTIMER_TEST") == "1")

    @classmethod
    def shutdown(cls, seconds: int = 0, force: bool = True) -> bool:
        """Schedules or executes Windows shutdown."""
        if cls.is_safe_mode():
            logging.info(f"[SAFETY SHIELD DRY_RUN] Simulated shutdown in {seconds}s (no real OS command executed)")
            return True

        try:
            cmd = ["shutdown", "-s", "-t", str(max(0, int(seconds)))]
            if force:
                cmd.append("-f")
            subprocess.Popen(cmd, creationflags=0x08000000)
            logging.info(f"Scheduled Windows shutdown in {seconds}s")
            return True
        except Exception as e:
            logging.error(f"Failed to schedule shutdown: {e}")
            return False

    @classmethod
    def restart(cls, seconds: int = 0, force: bool = True) -> bool:
        """Schedules or executes Windows restart."""
        if cls.is_safe_mode():
            logging.info(f"[SAFETY SHIELD DRY_RUN] Simulated restart in {seconds}s (no real OS command executed)")
            return True

        try:
            cmd = ["shutdown", "-r", "-t", str(max(0, int(seconds)))]
            if force:
                cmd.append("-f")
            subprocess.Popen(cmd, creationflags=0x08000000)
            logging.info(f"Scheduled Windows restart in {seconds}s")
            return True
        except Exception as e:
            logging.error(f"Failed to schedule restart: {e}")
            return False

    @classmethod
    def abort_shutdown(cls) -> bool:
        """Aborts any scheduled Windows shutdown/restart (shutdown -a)."""
        if cls.is_safe_mode():
            logging.info("[SAFETY SHIELD DRY_RUN] Simulated abort_shutdown (no real OS command executed)")
            return True

        try:
            subprocess.Popen(["shutdown", "-a"], creationflags=0x08000000)
            logging.info("Aborted Windows shutdown schedule (shutdown -a)")
            return True
        except Exception as e:
            logging.error(f"Failed to abort shutdown: {e}")
            return False

    @classmethod
    def sleep(cls) -> bool:
        """Suspends system into Sleep state."""
        if cls.is_safe_mode():
            logging.info("[SAFETY SHIELD DRY_RUN] Simulated system sleep (no real OS command executed)")
            return True

        try:
            logging.info("Triggering System Sleep (SetSuspendState)")
            res = ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            if res == 0:
                subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], creationflags=0x08000000)
            return True
        except Exception as e:
            logging.error(f"Failed to suspend system: {e}")
            return False

    @classmethod
    def lock(cls) -> bool:
        """Locks current Windows workstation session."""
        if cls.is_safe_mode():
            logging.info("[SAFETY SHIELD DRY_RUN] Simulated lock workstation (no real OS command executed)")
            return True

        try:
            logging.info("Triggering Workstation Lock (LockWorkStation)")
            res = ctypes.windll.user32.LockWorkStation()
            if res == 0:
                subprocess.Popen(["rundll32.exe", "user32.dll", "LockWorkStation"], creationflags=0x08000000)
            return True
        except Exception as e:
            logging.error(f"Failed to lock workstation: {e}")
            return False

    @classmethod
    def turn_off_monitors(cls) -> bool:
        """Powers off all connected displays without sleeping the PC."""
        if cls.is_safe_mode():
            logging.info("[SAFETY SHIELD DRY_RUN] Simulated turn off monitors (no real OS command executed)")
            return True

        try:
            logging.info("Powering off displays (SC_MONITORPOWER, 2)")
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF)
            return True
        except Exception as e:
            logging.error(f"Failed to turn off monitors: {e}")
            return False

    @classmethod
    def set_keep_awake(cls, enabled: bool = True) -> bool:
        """
        Enables or disables Caffeine / Keep-Awake mode to prevent Windows
        from automatically going to sleep while a task or timer is running.
        """
        if cls.is_safe_mode():
            logging.info(f"[SAFETY SHIELD DRY_RUN] Simulated set_keep_awake({enabled})")
            return True

        try:
            if enabled:
                flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
                ctypes.windll.kernel32.SetThreadExecutionState(flags)
                logging.info("Keep-Awake (Caffeine) mode ENABLED")
            else:
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
                logging.info("Keep-Awake (Caffeine) mode DISABLED")
            return True
        except Exception as e:
            logging.error(f"Failed to set Keep-Awake state: {e}")
            return False
