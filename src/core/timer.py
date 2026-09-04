"""
Core Timer Engine Module
Single Source of Truth for timing, countdowns, wall-clock scheduling, and action dispatching.
"""

import threading
import time
import datetime
import logging
from .power import PowerManager

class TimerEngine:
    VALID_MODES = {"shutdown", "restart", "sleep", "lock", "monitor"}

    def __init__(self, on_state_change=None):
        self.on_state_change = on_state_change
        self.is_active = False
        self.mode = "shutdown"
        self.trigger_type = "countdown" # "countdown" | "at_time"
        self.target_time_str = ""
        self.total_secs = 0
        self.rem_secs = 0
        self.keep_awake = False

        self._ticker_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    @staticmethod
    def calculate_secs_until(target_hour: int, target_minute: int) -> int:
        """Calculates difference in seconds from now until HH:MM (handling next-day wrap)."""
        now = datetime.datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target <= now:
            target += datetime.timedelta(days=1)
        delta_secs = int((target - now).total_seconds())
        return max(1, delta_secs)

    def start(self, mode: str, secs: int, trigger_type: str = "countdown", target_time_str: str = "", keep_awake: bool = False) -> dict:
        """Starts countdown timer with unified state management."""
        with self._lock:
            if mode not in self.VALID_MODES:
                return {"success": False, "error": f"Неизвестный режим: {mode}"}

            self.cancel_internal()

            self.mode = mode
            self.trigger_type = trigger_type
            self.target_time_str = target_time_str
            self.keep_awake = keep_awake

            if trigger_type == "at_time" and target_time_str:
                try:
                    parts = target_time_str.strip().split(":")
                    th, tm = int(parts[0]), int(parts[1])
                    secs = self.calculate_secs_until(th, tm)
                except Exception as e:
                    logging.error(f"Error parsing at_time '{target_time_str}': {e}")
                    return {"success": False, "error": "Неверный формат времени (ЧЧ:ММ)"}

            if secs <= 0:
                return {"success": False, "error": "Время должно быть больше нуля"}

            self.total_secs = secs
            self.rem_secs = secs
            self.is_active = True
            self._stop_event.clear()

            # Handle Keep-Awake
            if self.keep_awake:
                PowerManager.set_keep_awake(True)

            # Schedule Windows native timer as safety net if shutdown/restart
            if self.mode == "shutdown":
                PowerManager.shutdown(self.rem_secs)
            elif self.mode == "restart":
                PowerManager.restart(self.rem_secs)

            self._ticker_thread = threading.Thread(target=self._ticker_loop, daemon=True, name="TimerTickerThread")
            self._ticker_thread.start()

            logging.info(f"TimerEngine started: mode={mode}, secs={secs}, trigger={trigger_type}, keep_awake={keep_awake}")
            return {"success": True, "state": self.get_state()}

    def snooze(self, additional_mins: int) -> dict:
        """Adds minutes to current active timer and properly reschedules Windows shutdown."""
        with self._lock:
            if not self.is_active:
                return {"success": False, "error": "Таймер не запущен"}

            add_secs = additional_mins * 60
            self.rem_secs += add_secs
            self.total_secs += add_secs

            logging.info(f"TimerEngine SNOOZE: +{additional_mins}m -> New rem_secs={self.rem_secs}")

            # Crucial: Reschedule Windows OS timer to prevent premature shutdown!
            if self.mode in ("shutdown", "restart"):
                PowerManager.abort_shutdown()
                if self.mode == "shutdown":
                    PowerManager.shutdown(self.rem_secs)
                elif self.mode == "restart":
                    PowerManager.restart(self.rem_secs)

            return {"success": True, "state": self.get_state()}

    def cancel(self) -> dict:
        """Cancels active timer, aborts OS shutdown schedule and disables keep-awake."""
        with self._lock:
            self.cancel_internal()
            return {"success": True, "state": self.get_state()}

    def cancel_internal(self):
        """Internal cancellation without locking."""
        self.is_active = False
        self._stop_event.set()
        PowerManager.abort_shutdown()
        if self.keep_awake:
            PowerManager.set_keep_awake(False)
            self.keep_awake = False
        logging.info("TimerEngine cancelled.")

    def execute_action(self, target_mode=None):
        """Executes the chosen power action immediately."""
        act_mode = target_mode or self.mode
        logging.info(f"TimerEngine: Executing target action '{act_mode}'")
        self.cancel_internal()

        if act_mode == "shutdown":
            PowerManager.shutdown(0)
        elif act_mode == "restart":
            PowerManager.restart(0)
        elif act_mode == "sleep":
            PowerManager.sleep()
        elif act_mode == "lock":
            PowerManager.lock()
        elif act_mode == "monitor":
            PowerManager.turn_off_monitors()

    def _ticker_loop(self):
        while not self._stop_event.is_set():
            time.sleep(1.0)
            with self._lock:
                if not self.is_active:
                    break

                self.rem_secs -= 1
                if self.rem_secs <= 0:
                    logging.info("Timer countdown reached 0!")
                    self.execute_action()
                    break

    def get_state(self) -> dict:
        """Returns snapshot of current timer state for the UI."""
        return {
            "is_active": self.is_active,
            "mode": self.mode,
            "trigger_type": self.trigger_type,
            "rem_secs": max(0, self.rem_secs),
            "total_secs": max(1, self.total_secs),
            "warning_active": self.is_active and (0 < self.rem_secs <= 60),
            "keep_awake": self.keep_awake
        }
