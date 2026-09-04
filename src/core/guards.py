"""
Smart Guard Monitoring Module
Provides background worker guards for CPU Idle, Target Process exit, and Network Bandwidth drop.
"""

import threading
import time
import logging
import psutil

class SmartGuardManager:
    def __init__(self, on_trigger_action):
        self.on_trigger_action = on_trigger_action
        self._stop_event = threading.Event()
        self._active_thread = None
        self._active_guard_type = None

    def stop(self):
        """Stops any active guard thread safely."""
        self._stop_event.set()
        self._active_guard_type = None
        logging.info("SmartGuardManager: Stop signal sent to active guard threads.")

    @property
    def is_active(self) -> bool:
        return self._active_thread is not None and self._active_thread.is_alive() and not self._stop_event.is_set()

    @property
    def active_type(self):
        return self._active_guard_type

    def start_cpu_idle_guard(self, mode: str, threshold: float = 10.0, required_duration: int = 6):
        """Triggers action when CPU usage stays below threshold for required duration."""
        self.stop()
        self._stop_event.clear()
        self._active_guard_type = "cpu_idle"

        def worker():
            logging.info(f"CPU Idle Guard started (threshold < {threshold}%, duration={required_duration}s)")
            consecutive_low = 0
            while not self._stop_event.is_set():
                try:
                    cpu = psutil.cpu_percent(interval=2)
                    if cpu < threshold:
                        consecutive_low += 2
                        logging.debug(f"CPU usage {cpu}% is low ({consecutive_low}/{required_duration}s)")
                    else:
                        consecutive_low = 0

                    if consecutive_low >= required_duration:
                        logging.info(f"CPU Idle Guard triggered (CPU {cpu}% for {consecutive_low}s). Executing {mode}")
                        self.on_trigger_action(mode)
                        break
                except Exception as e:
                    logging.error(f"CPU Idle Guard exception: {e}")
                    time.sleep(2)

        self._active_thread = threading.Thread(target=worker, daemon=True, name="CPUIdleGuardThread")
        self._active_thread.start()

    def start_process_guard(self, mode: str, target_process: str):
        """Triggers action when the target process terminates."""
        self.stop()
        self._stop_event.clear()
        self._active_guard_type = "process_guard"

        def worker():
            logging.info(f"Process Guard started for: '{target_process}'")
            if not target_process:
                logging.error("Process Guard: Target process name empty!")
                return

            process_seen = False
            while not self._stop_event.is_set():
                running = False
                try:
                    for p in psutil.process_iter(['name']):
                        try:
                            p_name = p.info.get('name')
                            if p_name and p_name.lower() == target_process.lower():
                                running = True
                                process_seen = True
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                except Exception as e:
                    logging.error(f"Process Guard iteration error: {e}")

                if process_seen and not running:
                    logging.info(f"Process Guard: '{target_process}' has terminated! Executing {mode}")
                    self.on_trigger_action(mode)
                    break

                time.sleep(2.5)

        self._active_thread = threading.Thread(target=worker, daemon=True, name="ProcessGuardThread")
        self._active_thread.start()

    def start_network_guard(self, mode: str, threshold_kbps: float = 100.0, required_duration: int = 30):
        """Triggers action when incoming network traffic stays below threshold for required duration."""
        self.stop()
        self._stop_event.clear()
        self._active_guard_type = "network_guard"

        def worker():
            logging.info(f"Network Guard started (< {threshold_kbps} KB/s for {required_duration}s)")
            consecutive_low = 0
            try:
                last_bytes = psutil.net_io_counters().bytes_recv
            except Exception as e:
                logging.error(f"Failed to read net_io_counters: {e}")
                return

            while not self._stop_event.is_set():
                time.sleep(2)
                try:
                    current_bytes = psutil.net_io_counters().bytes_recv
                    speed_kbps = (current_bytes - last_bytes) / 1024.0 / 2.0
                    last_bytes = current_bytes

                    if speed_kbps < threshold_kbps:
                        consecutive_low += 2
                        logging.debug(f"Net speed {speed_kbps:.1f} KB/s < {threshold_kbps} KB/s ({consecutive_low}/{required_duration}s)")
                    else:
                        consecutive_low = 0

                    if consecutive_low >= required_duration:
                        logging.info(f"Network Guard triggered (Speed {speed_kbps:.1f} KB/s for {consecutive_low}s). Executing {mode}")
                        self.on_trigger_action(mode)
                        break
                except Exception as e:
                    logging.error(f"Network Guard exception: {e}")

        self._active_thread = threading.Thread(target=worker, daemon=True, name="NetworkGuardThread")
        self._active_thread.start()

    @staticmethod
    def get_running_process_names():
        """Returns clean list of currently running executable processes."""
        procs = set()
        system_ignores = {'system', 'idle', 'svchost.exe', 'csrss.exe', 'registry', 'smss.exe', 'services.exe', 'lsass.exe'}
        try:
            for p in psutil.process_iter(['name']):
                try:
                    name = p.info.get('name')
                    if name and name.endswith('.exe') and name.lower() not in system_ignores:
                        procs.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logging.error(f"Error enumerating running processes: {e}")
        return sorted(list(procs), key=lambda s: s.lower())
