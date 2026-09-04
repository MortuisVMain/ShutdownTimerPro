# ⚡ ShutdownTimerPro (Obsidian Studio 3.1)

[![Release](https://img.shields.io/badge/release-v0.3.1--alpha-orange.svg)](https://github.com/MortuisVMain/ShutdownTimerPro/releases)
[![Status](https://img.shields.io/badge/status-Alpha%20v0.3.1-blue.svg)](https://github.com/MortuisVMain/ShutdownTimerPro)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-pywebview%20%2B%20HTML5-cyan.svg)](https://pywebview.flowrl.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)](https://microsoft.com/windows)

A modern, precision PC Power Controller & Shutdown Timer featuring a **Raycast & Teenage Engineering-inspired Obsidian Studio UI**, complete timer preferences persistence, universal `Enter` launch hotkey, tactile stepper controls, and Smart Guard protections.

> 🚀 **Current Version**: **v0.3.1-alpha** (Obsidian Studio Craft UI, Preferences Persistence, Enter Hotkey Everywhere, Tactile Steppers, Zero Cheap Emojis).

---

## ✨ Features

- 💎 **Obsidian Studio Craft UI**: Bespoke, high-end dark studio aesthetic inspired by Teenage Engineering and Raycast: precision hairline borders (`rgba(255,255,255,0.08)`), jewel status LEDs, crisp digital chronometer (`JetBrains Mono`, `tabular-nums`), and 100% pixel-perfect vector SVG icons (zero cheap emojis).
- 💾 **State & Time Persistence**: Automatically remembers and restores your configured timer values (hours, minutes, target wall-clock time), chosen action mode, and smart guards across app restarts in `timer_cyber_prefs.json`.
- ⌨️ **Universal Enter Hotkey**: Press `Enter` or `NumpadEnter` anywhere (even while typing in time inputs) to instantly launch the timer or execute the action.
- 🎚️ **Tactile Micro-Steppers**: Dedicated `[-]` and `[+]` tactile buttons for smooth, one-click adjustments of hours and minutes, plus tactile preset keys (`15m`, `30m`, `45m`, `1h`, `2h`, `4h`).
- ⚡ **Immediate Action Execution**: Convenient "Выполнить выбранное действие сейчас" sub-action button for instant execution without waiting.
- 📊 **Real-time Telemetry Sampler**: Dedicated background sampling thread ensuring accurate, live CPU and RAM load percentages without 0% freezes.
- 🕒 **Dual Timing Modes**:
  - **⏱ Countdown ("Таймер")**: High-precision countdown with seconds readout (`00:30:00`).
  - **🕒 Wall-Clock ("Точное время")**: Schedule actions for an exact time (e.g. `02:30`) with automatic next-day delta calculation.
- ⚡ **5 Power Modes**:
  - ⏻ **Shutdown** (`shutdown -s`)
  - ☾ **Sleep** (`powrprof.dll,SetSuspendState`)
  - ⟳ **Restart** (`shutdown -r`)
  - 🔒 **Lock** (`user32.dll,LockWorkStation`)
  - 🖥️ **Turn Off Display / Monitor** (`SendMessage SC_MONITORPOWER, 2`) — powers off displays without sleeping the PC.
- ☕ **Caffeine / Keep-Awake Mode**: Prevents Windows from automatically sleeping during long downloads or video renders via Win32 `SetThreadExecutionState`.
- 🔒 **Single Instance Win32 Mutex**: Atomic instance lock via `CreateMutexW` and clean loopback restore signal.
- 🛡️ **Smart Guard Protections**:
  - **CPU Idle Guard**: Triggers action when CPU drops below threshold after heavy compiling or rendering.
  - **Process Guard**: Triggers action immediately when a selected `.exe` game or tool exits.
  - **Network Guard**: Triggers action when download bandwidth falls below threshold (< 100 KB/s).
- 📌 **System Tray Integration**: Minimize to Windows notification area with dynamic status tooltip and context menu.
- 🔊 **Audio Synthesizer & Beeps**: Analog-modeled Web Audio clicks, mute toggle, and a 10-second warning countdown audio cue.
- 🔄 **Safe Snooze**: Adding `+5m / +10m / +15m` safely aborts and reschedules the Windows OS shutdown timer without desync.

---

## 📥 Download Release (.exe)

Download the standalone executable directly from the [Releases Page](https://github.com/MortuisVMain/ShutdownTimerPro/releases/tag/v0.3.1-alpha):
- 📦 **[ShutdownTimerPro_v0.3.1-alpha.exe](https://github.com/MortuisVMain/ShutdownTimerPro/releases/download/v0.3.1-alpha/ShutdownTimerPro_v0.3.1-alpha.exe)**

---

## 🛠️ Architecture & Tests

See our Architecture Decision Records in [`docs/adr/001-timer-architecture-and-win32.md`](docs/adr/001-timer-architecture-and-win32.md).

```bash
# Run unit tests
python -m unittest discover -s tests -p "test_*.py"

# Run from source
python src/main.py
```

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).
