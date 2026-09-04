import webview
import os, sys, json, threading, time, ctypes, logging
import psutil
from PIL import Image
import pystray

# Add src to sys.path if needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.power import PowerManager
from core.mutex import SingleInstanceMutex
from core.guards import SmartGuardManager
from core.timer import TimerEngine

# Windows Taskbar App ID
try:
    myappid = "cyberhud.pctimer.app.0.3"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    logging.warning(f"Could not set AppUserModelID: {e}")

if getattr(sys, 'frozen', False):
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    PREFS_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = CURRENT_DIR
    PREFS_DIR = APP_DIR

SAVE_FILE = os.path.join(PREFS_DIR, "timer_cyber_prefs.json")
LOG_FILE = os.path.join(PREFS_DIR, "app.log")
GUI_DIR = os.path.join(APP_DIR, "gui") if os.path.exists(os.path.join(APP_DIR, "gui")) else APP_DIR
HTML_FILE = os.path.join(GUI_DIR, "index.html")
ICON_FILE = os.path.join(GUI_DIR, "app_icon.png")

# Setup Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    encoding="utf-8"
)

def log_info(msg):
    logging.info(msg)
    print(f"[INFO] {msg}")

def log_error(msg):
    logging.error(msg)
    print(f"[ERROR] {msg}")

DEFAULT_PREFS = {
    "x": None,
    "y": None,
    "sound_muted": False,
    "keep_awake": False,
    "hours": 0,
    "minutes": 30,
    "at_time": "23:30",
    "time_type": "countdown",
    "mode": "shutdown",
    "guard": "normal",
    "guard_param": ""
}

log_info("--- Запуск ShutdownTimerPro v0.3.1-alpha ---")

def load_prefs():
    prefs = dict(DEFAULT_PREFS)
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    prefs.update(data)
    except Exception as e:
        log_error(f"Ошибка загрузки настроек: {e}")
    return prefs

def save_prefs(updated_dict: dict):
    try:
        current = load_prefs()
        if isinstance(updated_dict, dict):
            current.update(updated_dict)
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"Ошибка сохранения настроек: {e}")

class TelemetrySampler:
    """Dedicated background sampler ensuring accurate, non-zero CPU and RAM metrics."""
    def __init__(self):
        self.cpu = 0.0
        self.ram = 0.0
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True, name="TelemetrySamplerThread")

    def start(self):
        try:
            psutil.cpu_percent(interval=None) # prime
        except Exception as e:
            log_error(f"Prime cpu_percent failed: {e}")
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _sample_loop(self):
        while not self._stop_event.is_set():
            try:
                c = psutil.cpu_percent(interval=1.0)
                r = psutil.virtual_memory().percent
                self.cpu = c
                self.ram = r
            except Exception as e:
                log_error(f"TelemetrySampler error: {e}")
                time.sleep(1.0)

    def get_stats(self):
        cpu_val = max(1, int(round(self.cpu))) if self.cpu > 0.4 else int(round(self.cpu))
        return {
            "cpu": cpu_val,
            "ram": int(round(self.ram))
        }

class CyberAPI:
    def __init__(self):
        self._window = None
        self._tray_icon = None
        self.sound_muted = False
        self.keep_awake = False

        prefs = load_prefs()
        self.sound_muted = prefs.get("sound_muted", False)
        self.keep_awake = prefs.get("keep_awake", False)

        # Initialize core managers & telemetry
        self.timer_engine = TimerEngine()
        self.guard_manager = SmartGuardManager(on_trigger_action=self.on_guard_triggered)
        self.telemetry = TelemetrySampler()
        self.telemetry.start()

    def set_window(self, window):
        self._window = window
        self._window.events.closed += self.on_window_closed

    def set_tray_icon(self, tray_icon):
        self._tray_icon = tray_icon

    def on_window_closed(self):
        log_info("Событие закрытия окна (closed)")
        self.cleanup_and_exit()

    def on_guard_triggered(self, mode):
        log_info(f"CyberAPI: Guard сработал! Запуск действия {mode}")
        self.timer_engine.execute_action(mode)
        if self._tray_icon:
            self._tray_icon.title = "ShutdownTimerPro | Готов"

    # --- Live System Telemetry & Process Info ---
    def get_system_stats(self):
        return self.telemetry.get_stats()

    def get_running_processes(self):
        return SmartGuardManager.get_running_process_names()

    # --- Timer & Action Endpoints ---
    def start_timer(self, mode: str, secs: int, trigger_type: str = "countdown", target_time_str: str = "", keep_awake: bool = False, hours: int = 0, minutes: int = 0):
        log_info(f"API start_timer: mode={mode}, secs={secs}, trigger={trigger_type}, time={target_time_str}, keep_awake={keep_awake}, h={hours}, m={minutes}")
        save_prefs({
            "mode": mode,
            "time_type": trigger_type,
            "at_time": target_time_str,
            "hours": hours,
            "minutes": minutes,
            "keep_awake": keep_awake
        })
        self.guard_manager.stop()
        res = self.timer_engine.start(mode, secs, trigger_type, target_time_str, keep_awake)
        if self._tray_icon and res.get("success"):
            self._tray_icon.title = f"ShutdownTimerPro | Активен ({mode.upper()})"
        return res

    def start_guard(self, mode: str, guard_type: str, guard_param=None, keep_awake: bool = False):
        log_info(f"API start_guard: mode={mode}, guard={guard_type}, param={guard_param}, keep_awake={keep_awake}")
        save_prefs({
            "mode": mode,
            "guard": guard_type,
            "guard_param": str(guard_param) if guard_param else "",
            "keep_awake": keep_awake
        })
        self.timer_engine.cancel()
        if keep_awake:
            PowerManager.set_keep_awake(True)

        if guard_type == "cpu_idle":
            self.guard_manager.start_cpu_idle_guard(mode)
        elif guard_type == "process_guard":
            proc_name = str(guard_param) if guard_param else ""
            if not proc_name:
                return {"success": False, "error": "Не указан процесс для мониторинга!"}
            self.guard_manager.start_process_guard(mode, proc_name)
        elif guard_type == "network_guard":
            limit = float(guard_param) if guard_param and str(guard_param).isdigit() else 100.0
            self.guard_manager.start_network_guard(mode, threshold_kbps=limit)
        else:
            return {"success": False, "error": f"Неизвестный тип гарда: {guard_type}"}

        if self._tray_icon:
            self._tray_icon.title = f"ShutdownTimerPro | Защита ({guard_type})"
        return {"success": True}

    def snooze(self, additional_mins: int):
        log_info(f"API snooze: +{additional_mins} мин")
        return self.timer_engine.snooze(additional_mins)

    def cancel_timer(self):
        log_info("API cancel_timer")
        self.guard_manager.stop()
        res = self.timer_engine.cancel()
        if self._tray_icon:
            self._tray_icon.title = "ShutdownTimerPro | Готов"
        return res

    def execute_action_now(self, mode: str):
        log_info(f"API execute_action_now: {mode}")
        self.guard_manager.stop()
        self.timer_engine.execute_action(mode)
        return {"success": True}

    def get_timer_state(self):
        state = self.timer_engine.get_state()
        state["guard_active"] = self.guard_manager.is_active
        state["guard_type"] = self.guard_manager.active_type
        return state

    # --- Preferences & Window Controls ---
    def get_user_prefs(self):
        return load_prefs()

    def save_user_prefs(self, prefs: dict):
        if isinstance(prefs, dict):
            save_prefs(prefs)
            if "sound_muted" in prefs:
                self.sound_muted = bool(prefs["sound_muted"])
            if "keep_awake" in prefs:
                self.keep_awake = bool(prefs["keep_awake"])
                PowerManager.set_keep_awake(self.keep_awake)
            return {"success": True}
        return {"success": False, "error": "Invalid prefs format"}

    def get_sound_muted(self):
        return self.sound_muted

    def set_sound_muted(self, muted: bool):
        self.sound_muted = bool(muted)
        save_prefs({"sound_muted": self.sound_muted})

    def get_keep_awake(self):
        return self.keep_awake

    def set_keep_awake(self, enabled: bool):
        self.keep_awake = bool(enabled)
        PowerManager.set_keep_awake(self.keep_awake)
        save_prefs({"keep_awake": self.keep_awake})

    def move_window(self, dx: int, dy: int):
        if self._window:
            nx = self._window.x + dx
            ny = self._window.y + dy
            self._window.move(nx, ny)
            save_prefs({"x": nx, "y": ny})

    def minimize(self):
        if self._window:
            self._window.minimize()

    def restore_window(self):
        if self._window:
            try:
                self._window.restore()
                self._window.show()
                self._window.activate()
            except Exception as e:
                log_error(f"Ошибка при фокусе окна: {e}")

    def close(self):
        if self._window:
            save_prefs({"x": self._window.x, "y": self._window.y})
            self._window.destroy()

    def cleanup_and_exit(self):
        log_info("Завершение работы ShutdownTimerPro...")
        self.cancel_timer()
        self.telemetry.stop()
        PowerManager.set_keep_awake(False)
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception as e:
                log_error(f"Ошибка остановки трея: {e}")

def create_tray_icon(api):
    try:
        if os.path.exists(ICON_FILE):
            image = Image.open(ICON_FILE)
        else:
            image = Image.new('RGB', (64, 64), color=(0, 242, 254))

        menu = pystray.Menu(
            pystray.MenuItem("👁️ Показать HUD", lambda: api.restore_window()),
            pystray.MenuItem("✕ Отменить таймер", lambda: api.cancel_timer()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚪 Выйти", lambda: api.close())
        )

        icon = pystray.Icon("ShutdownTimerPro", image, "ShutdownTimerPro | Готов", menu)
        return icon
    except Exception as e:
        log_error(f"Ошибка создания иконки трея: {e}")
        return None

def main():
    # 1. Atomic Win32 Named Mutex Check
    mutex = SingleInstanceMutex()
    if not mutex.acquire():
        log_info("Приложение уже запущено. Активация существующего окна...")
        mutex.notify_running_instance()
        sys.exit(0)

    api = CyberAPI()
    mutex.listen_for_restore(callback=api.restore_window)

    prefs = load_prefs()
    px, py = prefs.get("x"), prefs.get("y")

    url = f"file:///{HTML_FILE.replace('\\', '/')}"

    kwargs = {
        "title": "ShutdownTimerPro v0.3.1-alpha",
        "url": url,
        "width": 430,
        "height": 790,
        "frameless": True,
        "transparent": False,
        "on_top": True,
        "js_api": api
    }
    if px is not None and py is not None:
        kwargs["x"] = px
        kwargs["y"] = py

    window = webview.create_window(**kwargs)
    api.set_window(window)

    # 2. System Tray
    tray_icon = create_tray_icon(api)
    if tray_icon:
        api.set_tray_icon(tray_icon)
        tray_thread = threading.Thread(target=tray_icon.run, daemon=True, name="TrayThread")
        tray_thread.start()

    try:
        webview.start()
    finally:
        mutex.release()
        api.cleanup_and_exit()

if __name__ == "__main__":
    main()
