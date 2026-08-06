import webview
import subprocess, os, sys, json, threading, time, ctypes
import psutil

# Windows Taskbar App ID
try:
    myappid = "cyberhud.pctimer.app.0.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

if getattr(sys, 'frozen', False):
    APP_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    PREFS_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    PREFS_DIR = APP_DIR

SAVE_FILE = os.path.join(PREFS_DIR, "timer_cyber_prefs.json")
GUI_DIR = os.path.join(APP_DIR, "gui") if os.path.exists(os.path.join(APP_DIR, "gui")) else APP_DIR
HTML_FILE = os.path.join(GUI_DIR, "index.html")

def load_prefs():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"x": None, "y": None}

def save_prefs(x, y):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"x": x, "y": y}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

class CyberAPI:
    def __init__(self):
        self._window = None
        self._guard_active = False

    def set_window(self, window):
        self._window = window

    def get_system_stats(self):
        return {
            "cpu": int(psutil.cpu_percent(interval=None)),
            "ram": int(psutil.virtual_memory().percent)
        }

    def move_window(self, dx, dy):
        if self._window:
            nx = self._window.x + dx
            ny = self._window.y + dy
            self._window.move(nx, ny)
            save_prefs(nx, ny)

    def minimize(self):
        if self._window:
            self._window.minimize()

    def close(self):
        if self._window:
            save_prefs(self._window.x, self._window.y)
            self._window.destroy()

    def launch_action(self, mode, secs, guard="normal"):
        self._guard_active = True
        
        if guard == "cpu_idle":
            threading.Thread(target=self._cpu_guard_thread, args=(mode,), daemon=True).start()
        else:
            if mode == "shutdown":
                subprocess.Popen(["shutdown", "-s", "-t", str(secs)], creationflags=0x08000000)
            elif mode == "restart":
                subprocess.Popen(["shutdown", "-r", "-t", str(secs)], creationflags=0x08000000)

    def _cpu_guard_thread(self, mode):
        while self._guard_active:
            cpu = psutil.cpu_percent(interval=2)
            if cpu < 10:
                self.execute_action(mode)
                break

    def execute_action(self, mode):
        if mode == "sleep":
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], creationflags=0x08000000)
        elif mode == "lock":
            subprocess.Popen(["rundll32.exe", "user32.dll", "LockWorkStation"], creationflags=0x08000000)
        elif mode == "shutdown":
            subprocess.Popen(["shutdown", "-s", "-t", "0"], creationflags=0x08000000)
        elif mode == "restart":
            subprocess.Popen(["shutdown", "-r", "-t", "0"], creationflags=0x08000000)

    def cancel_action(self):
        self._guard_active = False
        try:
            subprocess.Popen(["shutdown", "-a"], creationflags=0x08000000)
        except Exception:
            pass

def main():
    api = CyberAPI()
    prefs = load_prefs()
    px, py = prefs.get("x"), prefs.get("y")

    url = f"file:///{HTML_FILE.replace('\\', '/')}"

    kwargs = {
        "title": "ПК Таймер Ultra Pro HUD",
        "url": url,
        "width": 420,
        "height": 740,
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
    webview.start()

if __name__ == "__main__":
    main()
