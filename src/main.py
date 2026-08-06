import webview
import subprocess, os, sys, json, threading, time, ctypes, socket, logging
import psutil
from PIL import Image
import pystray

# Windows Taskbar App ID
try:
    myappid = "cyberhud.pctimer.app.0.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

SINGLE_INSTANCE_PORT = 49812

if getattr(sys, 'frozen', False):
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    PREFS_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
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

log_info("--- Запуск ShutdownTimerPro ---")

def load_prefs():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {
                        "x": data.get("x"),
                        "y": data.get("y"),
                        "sound_muted": bool(data.get("sound_muted", False))
                    }
    except Exception as e:
        log_error(f"Ошибка загрузки настроек: {e}")
    return {"x": None, "y": None, "sound_muted": False}

def save_prefs(x, y, sound_muted=False):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"x": x, "y": y, "sound_muted": sound_muted}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"Ошибка сохранения настроек: {e}")

class SingleInstanceLock:
    def __init__(self, port=SINGLE_INSTANCE_PORT):
        self.port = port
        self.server_socket = None
        self.is_single = False

    def acquire(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("127.0.0.1", self.port))
            self.server_socket.listen(1)
            self.is_single = True
            return True
        except socket.error:
            self.is_single = False
            return False

    def notify_running_instance(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", self.port))
            client.sendall(b"RESTORE")
            client.close()
        except Exception as e:
            log_error(f"Ошибка отправки сигнала существующему экземпляру: {e}")

    def listen_for_signals(self, restore_callback):
        def listener():
            while self.is_single and self.server_socket:
                try:
                    conn, _ = self.server_socket.accept()
                    data = conn.recv(1024)
                    if data == b"RESTORE":
                        log_info("Получен сигнал восстановления окна от дублирующего процесса")
                        restore_callback()
                    conn.close()
                except Exception:
                    break
        t = threading.Thread(target=listener, daemon=True)
        t.start()

    def release(self):
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

class CyberAPI:
    def __init__(self):
        self._window = None
        self._guard_active = False
        self._stop_event = threading.Event()
        self._guard_thread = None
        self._tray_icon = None
        self.sound_muted = False
        prefs = load_prefs()
        self.sound_muted = prefs.get("sound_muted", False)

    def set_window(self, window):
        self._window = window
        self._window.events.closed += self.on_window_closed

    def set_tray_icon(self, tray_icon):
        self._tray_icon = tray_icon

    def on_window_closed(self):
        log_info("Событие закрытия окна (closed)")
        self.cleanup_and_exit()

    def get_system_stats(self):
        try:
            return {
                "cpu": int(psutil.cpu_percent(interval=None)),
                "ram": int(psutil.virtual_memory().percent)
            }
        except Exception as e:
            return {"cpu": 0, "ram": 0}

    def get_running_processes(self):
        """Возвращает отсортированный список именованных .exe процессов"""
        try:
            procs = set()
            for p in psutil.process_iter(['name']):
                name = p.info.get('name')
                if name and name.endswith('.exe') and name.lower() not in ['system', 'idle', 'svchost.exe', 'csrss.exe']:
                    procs.add(name)
            return sorted(list(procs), key=lambda s: s.lower())
        except Exception as e:
            log_error(f"Ошибка получения списка процессов: {e}")
            return []

    def move_window(self, dx, dy):
        if self._window:
            nx = self._window.x + dx
            ny = self._window.y + dy
            self._window.move(nx, ny)
            save_prefs(nx, ny, self.sound_muted)

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
            save_prefs(self._window.x, self._window.y, self.sound_muted)
            self._window.destroy()

    def get_sound_muted(self):
        return self.sound_muted

    def set_sound_muted(self, muted):
        self.sound_muted = bool(muted)
        if self._window:
            save_prefs(self._window.x, self._window.y, self.sound_muted)

    def launch_action(self, mode, secs, guard="normal", guard_param=None):
        # Strict Input Validation
        valid_modes = {"shutdown", "restart", "sleep", "lock"}
        if mode not in valid_modes:
            err = f"Невалидный режим действия: {mode}"
            log_error(err)
            return {"success": False, "error": err}

        if not isinstance(secs, int) or secs < 0 or secs > 86400:
            err = f"Невалидное значение времени (0-86400): {secs}"
            log_error(err)
            return {"success": False, "error": err}

        valid_guards = {"normal", "cpu_idle", "process_guard", "network_guard"}
        if guard not in valid_guards:
            err = f"Невалидный режим Smart Guard: {guard}"
            log_error(err)
            return {"success": False, "error": err}

        self._guard_active = True
        self._stop_event.clear()
        log_info(f"Запуск таймера/гарда: mode={mode}, secs={secs}, guard={guard}, param={guard_param}")

        if self._tray_icon:
            self._tray_icon.title = f"ShutdownTimerPro | Активен ({mode.upper()})"

        if guard == "cpu_idle":
            self._guard_thread = threading.Thread(target=self._cpu_guard_thread, args=(mode,), daemon=True)
            self._guard_thread.start()
        elif guard == "process_guard":
            proc_name = str(guard_param) if guard_param else ""
            self._guard_thread = threading.Thread(target=self._process_guard_thread, args=(mode, proc_name), daemon=True)
            self._guard_thread.start()
        elif guard == "network_guard":
            speed_limit = int(guard_param) if guard_param and str(guard_param).isdigit() else 100
            self._guard_thread = threading.Thread(target=self._network_guard_thread, args=(mode, speed_limit), daemon=True)
            self._guard_thread.start()
        else:
            if mode == "shutdown":
                return self._run_sys_cmd(["shutdown", "-s", "-t", str(secs)])
            elif mode == "restart":
                return self._run_sys_cmd(["shutdown", "-r", "-t", str(secs)])

        return {"success": True}

    def _cpu_guard_thread(self, mode):
        log_info("Запущен CPU Guard thread (ожидание CPU < 10%)")
        while self._guard_active and not self._stop_event.is_set():
            cpu = psutil.cpu_percent(interval=2)
            if cpu < 10:
                log_info(f"CPU Guard сработал (CPU {cpu}% < 10%). Выполнение action={mode}")
                self.execute_action(mode)
                break

    def _process_guard_thread(self, mode, target_process):
        log_info(f"Запущен Process Guard thread для процесса: '{target_process}'")
        if not target_process:
            log_error("Process Guard: не указано имя процесса!")
            return

        process_seen = False
        while self._guard_active and not self._stop_event.is_set():
            running = False
            for p in psutil.process_iter(['name']):
                if p.info.get('name') and p.info['name'].lower() == target_process.lower():
                    running = True
                    process_seen = True
                    break
            
            if process_seen and not running:
                log_info(f"Process Guard: процесс '{target_process}' завершился! Выполнение action={mode}")
                self.execute_action(mode)
                break
            
            time.sleep(3)

    def _network_guard_thread(self, mode, threshold_kbps=100, duration_sec=15):
        log_info(f"Запущен Network Guard thread (< {threshold_kbps} KB/s в течение {duration_sec}s)")
        low_speed_count = 0
        last_bytes = psutil.net_io_counters().bytes_recv

        while self._guard_active and not self._stop_event.is_set():
            time.sleep(2)
            current_bytes = psutil.net_io_counters().bytes_recv
            speed_kbps = (current_bytes - last_bytes) / 1024.0 / 2.0
            last_bytes = current_bytes

            if speed_kbps < threshold_kbps:
                low_speed_count += 2
            else:
                low_speed_count = 0

            if low_speed_count >= duration_sec:
                log_info(f"Network Guard сработал (скорость {speed_kbps:.1f} KB/s < {threshold_kbps} KB/s). Выполнение action={mode}")
                self.execute_action(mode)
                break

    def execute_action(self, mode):
        log_info(f"Выполнение итогового действия: {mode}")
        self._guard_active = False

        if mode == "sleep":
            return self._run_sys_cmd(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        elif mode == "lock":
            return self._run_sys_cmd(["rundll32.exe", "user32.dll", "LockWorkStation"])
        elif mode == "shutdown":
            return self._run_sys_cmd(["shutdown", "-s", "-t", "0"])
        elif mode == "restart":
            return self._run_sys_cmd(["shutdown", "-r", "-t", "0"])
        return {"success": True}

    def cancel_action(self):
        log_info("Отмена таймера / выключения (shutdown -a)")
        self._guard_active = False
        self._stop_event.set()
        if self._tray_icon:
            self._tray_icon.title = "ShutdownTimerPro | Готов"
        return self._run_sys_cmd(["shutdown", "-a"])

    def _run_sys_cmd(self, cmd_args):
        try:
            subprocess.Popen(cmd_args, creationflags=0x08000000)
            return {"success": True}
        except PermissionError as pe:
            err = f"Ошибка прав доступа (Administrator required): {pe}"
            log_error(err)
            return {"success": False, "error": "Недостаточно прав администратора для выполнения команды!"}
        except Exception as e:
            err = f"Ошибка выполнения команды {' '.join(cmd_args)}: {e}"
            log_error(err)
            return {"success": False, "error": str(e)}

    def cleanup_and_exit(self):
        log_info("Завершение работы ShutdownTimerPro")
        if self._guard_active:
            self.cancel_action()
        self._stop_event.set()
        if self._window:
            try:
                save_prefs(self._window.x, self._window.y, self.sound_muted)
            except Exception:
                pass
        if self._tray_icon:
            try:
                self._tray_icon.stop()
            except Exception:
                pass

def create_tray_icon(api):
    try:
        if os.path.exists(ICON_FILE):
            image = Image.open(ICON_FILE)
        else:
            image = Image.new('RGB', (64, 64), color=(0, 242, 254))
        
        menu = pystray.Menu(
            pystray.MenuItem("👁️ Показать HUD", lambda: api.restore_window()),
            pystray.MenuItem("✕ Отменить таймер", lambda: api.cancel_action()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚪 Выйти", lambda: api.close())
        )
        
        icon = pystray.Icon("ShutdownTimerPro", image, "ShutdownTimerPro | Готов", menu)
        return icon
    except Exception as e:
        log_error(f"Ошибка создания иконки трея: {e}")
        return None

def main():
    # 1. Single Instance Check
    lock = SingleInstanceLock()
    if not lock.acquire():
        log_info("Приложение уже запущено. Отправка сигнала фокусировки...")
        lock.notify_running_instance()
        sys.exit(0)

    api = CyberAPI()
    lock.listen_for_signals(restore_callback=api.restore_window)

    prefs = load_prefs()
    px, py = prefs.get("x"), prefs.get("y")

    url = f"file:///{HTML_FILE.replace('\\', '/')}"

    kwargs = {
        "title": "ПК Таймер Ultra Pro HUD",
        "url": url,
        "width": 420,
        "height": 760,
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

    # 2. Start Tray Icon in background thread
    tray_icon = create_tray_icon(api)
    if tray_icon:
        api.set_tray_icon(tray_icon)
        tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
        tray_thread.start()

    try:
        webview.start()
    finally:
        lock.release()
        api.cleanup_and_exit()

if __name__ == "__main__":
    main()
