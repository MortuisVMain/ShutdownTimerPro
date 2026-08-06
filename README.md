# ⚡ ShutdownTimerPro (ПК Таймер Ultra Pro HUD)

[![Release](https://img.shields.io/badge/release-v0.9.0--beta-orange.svg)](https://github.com/MortuisVMain/ShutdownTimerPro/releases)
[![Status](https://img.shields.io/badge/status-Beta%20Preview-yellow.svg)](https://github.com/MortuisVMain/ShutdownTimerPro)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-pywebview%20%2B%20HTML5-cyan.svg)](https://pywebview.flowrl.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg)](https://microsoft.com/windows)

A modern, high-tech PC Shutdown Timer & Power Manager featuring a **Cyber HUD Interface**, real-time hardware telemetry (CPU & RAM), web audio effects, and Smart Guard protections.

> 🚧 **Note**: This project is currently in active **Beta Development (v0.9.0-beta)**. New features, improvements, and UI refinements are continuously being added.

---

## ✨ Features

- 🖥️ **Cyber HUD Interface**: Frameless, sleek Glassmorphism UI built with PyWebview, HTML5, CSS3, and Google Outfit/JetBrains Mono fonts.
- 📊 **Real-time Hardware Telemetry**: Live CPU and RAM load monitoring built into the main dashboard.
- 🛡️ **Smart Guard Protection**:
  - **Normal Timer**: Traditional countdown timer for specified hours & minutes.
  - **CPU Idle Guard**: Automatically triggers power action after heavy tasks finish (e.g. video rendering or compiling) when CPU usage drops below 10%.
- ⚡ **Quick Presets & Snooze**:
  - Presets: 15m, 30m, 1.5h, 2h.
  - Quick Snooze buttons (+5m, +10m, +15m).
- 🚨 **Fullscreen Warning Overlay**: Visual 60-second countdown warning before executing shutdown/sleep/restart actions.
- 🔊 **Web Audio Synthesizer**: Built-in Sci-Fi audio feedback for interactions using the Web Audio API.
- ⚡ **4 Power Modes**:
  - ⏻ **Shutdown** (`shutdown -s`)
  - ☾ **Sleep** (`powrprof.dll,SetSuspendState`)
  - ⟳ **Restart** (`shutdown -r`)
  - 🔒 **Lock** (`user32.dll,LockWorkStation`)

---

## 📥 Download Beta (.exe)

You can download the pre-compiled standalone **v0.9.0-beta** `.exe` file directly from the [Releases](https://github.com/MortuisVMain/ShutdownTimerPro/releases) page. No Python installation required!

---

## 🛠️ Installation & Running from Source

### Prerequisites
- Python 3.10+
- Windows 10 / 11

### 1. Clone the repository
```bash
git clone https://github.com/MortuisVMain/ShutdownTimerPro.git
cd ShutdownTimerPro
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python src/main.py
```

---

## 📦 Building Standalone Executable (.exe)

To compile the application into a single standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --icon="src/assets/app_icon.ico" --add-data "src/gui;gui" --name "ShutdownTimerPro" src/main.py
```

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).
