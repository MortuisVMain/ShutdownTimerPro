# ⚡ ShutdownTimerPro (ПК Таймер Ultra Pro HUD 2.0)

[![Release](https://img.shields.io/badge/release-v0.2.0--alpha-orange.svg)](https://github.com/MortuisVMain/ShutdownTimerPro/releases)
[![Status](https://img.shields.io/badge/status-Alpha%20v0.2.0-blue.svg)](https://github.com/MortuisVMain/ShutdownTimerPro)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-pywebview%20%2B%20HTML5-cyan.svg)](https://pywebview.flowrl.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)](https://microsoft.com/windows)

A modern, high-tech PC Shutdown Timer & Power Manager featuring a **Cyber HUD 2.0 Interface**, real-time hardware telemetry (CPU & RAM), web audio synthesizer, and Smart Guard protections.

> 🚀 **Current Version**: **v0.2.0-alpha** (Modular Win32 Core, Wall-Clock mode, Monitor Power, Keep-Awake).

---

## ✨ Features

- 🖥️ **Cyber HUD 2.0 Interface**: Sleek Glassmorphism UI with smooth native dragging (`-webkit-app-region: drag`), offline font fallbacks, and real-time state polling.
- 🕒 **Dual Timing Modes**:
  - **⏱ Countdown ("Через время")**: Classic countdown for specified hours and minutes.
  - **🕒 Wall-Clock ("В точное время")**: Schedule actions for an exact time (e.g. `02:30`), with automatic next-day delta calculation.
- ⚡ **5 Power Modes**:
  - ⏻ **Shutdown** (`shutdown -s`)
  - ☾ **Sleep** (`powrprof.dll,SetSuspendState`)
  - ⟳ **Restart** (`shutdown -r`)
  - 🔒 **Lock** (`user32.dll,LockWorkStation`)
  - 🖥️ **Turn Off Display / Monitor** (`SendMessage SC_MONITORPOWER, 2`) — powers off displays without suspending the PC.
- ☕ **Caffeine / Keep-Awake Mode**: Prevents Windows from automatically sleeping during long downloads or video renders via Win32 `SetThreadExecutionState`.
- 🔒 **Single Instance Win32 Mutex**: Atomic instance lock via `CreateMutexW` and clean loopback restore signal.
- 🛡️ **Smart Guard Protections**:
  - **CPU Idle Guard**: Triggers action when CPU drops below threshold after heavy compiling or rendering.
  - **Process Guard**: Triggers action immediately when a selected `.exe` game or tool exits.
  - **Network Guard**: Triggers action when download bandwidth falls below threshold (< 100 KB/s).
- 📌 **System Tray Integration**: Minimize to Windows notification area with dynamic status tooltip and context menu.
- 🔊 **Audio Synthesizer & Beeps**: Sci-Fi Web Audio clicks, mute toggle, and a 10-second warning countdown audio cue.
- ⌨️ **Keyboard Hotkeys**: `Space` (Start / Pause), `Esc` (Cancel timer).
- 🔄 **Safe Snooze**: Adding `+5m / +10m / +15m` safely aborts and reschedules the Windows OS shutdown timer without desync.

---

## 📥 Download Release (.exe)

Download the standalone standalone executable directly from the [Releases Page](https://github.com/MortuisVMain/ShutdownTimerPro/releases/tag/v0.2.0-alpha):
- 📦 **[ShutdownTimerPro_v0.2.0-alpha.exe](https://github.com/MortuisVMain/ShutdownTimerPro/releases/download/v0.2.0-alpha/ShutdownTimerPro_v0.2.0-alpha.exe)**

---

## 🛠️ Architecture

See our Architecture Decision Records in [`docs/adr/001-timer-architecture-and-win32.md`](docs/adr/001-timer-architecture-and-win32.md) for details on the Single Source of Truth `TimerEngine` and Win32 integration.

```bash
# Run unit tests
python -m unittest discover -s tests -p "test_*.py"

# Run from source
python src/main.py
```

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).
