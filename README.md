# ⚡ ShutdownTimerPro (ПК Таймер Ultra Pro HUD)

[![Release](https://img.shields.io/badge/release-v0.1.1--alpha-orange.svg)](https://github.com/MortuisVMain/ShutdownTimerPro/releases)
[![Status](https://img.shields.io/badge/status-Early%20Alpha-red.svg)](https://github.com/MortuisVMain/ShutdownTimerPro)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-pywebview%20%2B%20HTML5-cyan.svg)](https://pywebview.flowrl.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)](https://microsoft.com/windows)

A modern, high-tech PC Shutdown Timer & Power Manager featuring a **Cyber HUD Interface**, real-time hardware telemetry (CPU & RAM), web audio effects, and Smart Guard protections.

> 🚧 **Note**: Current Version: **v0.1.1-alpha**.

---

## ✨ Features

- 🖥️ **Cyber HUD Interface**: Frameless, sleek Glassmorphism UI built with PyWebview, HTML5, CSS3, and Google Outfit/JetBrains Mono fonts.
- 🔒 **Single Instance Lock**: Prevents duplicate app instances and focuses the existing window on second launch.
- 📌 **System Tray Integration**: Minimize to Windows tray with dynamic tooltip and context menu (Show, Cancel, Exit).
- 📊 **Real-time Hardware Telemetry**: Live CPU and RAM load monitoring built into the main dashboard.
- 🛡️ **Smart Guard Protections**:
  - **Normal Timer**: Traditional countdown timer for specified hours & minutes.
  - **CPU Idle Guard**: Triggers action when CPU drops below 10% after heavy rendering/compiling.
  - **Process Guard**: Triggers action immediately when a target `.exe` process closes (games, renders).
  - **Network Guard**: Triggers action when download speed drops below threshold (< 100 KB/s).
- 🔊 **Audio Controls & Beeps**: Mute toggle button and countdown audio beeps for the last 10 seconds.
- ⌨️ **Keyboard Hotkeys**: `Space` to start/pause timer, `Esc` to cancel timer.
- ⚡ **4 Power Modes**:
  - ⏻ **Shutdown** (`shutdown -s`)
  - ☾ **Sleep** (`powrprof.dll,SetSuspendState`)
  - ⟳ **Restart** (`shutdown -r`)
  - 🔒 **Lock** (`user32.dll,LockWorkStation`)

---

## 📥 Download Release (.exe)

Download the pre-compiled standalone executable directly from the [Releases Page](https://github.com/MortuisVMain/ShutdownTimerPro/releases/tag/v0.1.1-alpha):
- 📦 **[ShutdownTimerPro_v0.1.1-alpha.exe](https://github.com/MortuisVMain/ShutdownTimerPro/releases/download/v0.1.1-alpha/ShutdownTimerPro_v0.1.1-alpha.exe)**

---

## 🛠️ Installation & Running from Source

```bash
git clone https://github.com/MortuisVMain/ShutdownTimerPro.git
cd ShutdownTimerPro
pip install -r requirements.txt
python src/main.py
```

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).
