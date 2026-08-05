# NeeWiFi: Linux WiFi Troubleshooter & Fixer 📡🛠️

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Linux-red.svg)]()
[![Cybersecurity Tool](https://img.shields.io/badge/Cybersecurity-Network--Repair-purple.svg)]()

**NeeWiFi** is a lightweight, interactive terminal utility designed to diagnose and repair common wireless network issues in Linux (specifically Kali Linux, Debian, and Ubuntu). If your wireless card is soft-blocked, network configurations are corrupted, or DNS settings are frozen, NeeWiFi scans your adapters and repairs them in one click.

---

## 📸 Diagnostic Console Preview
![NeeWiFi Terminal Mockup](./assets/neewifi_dashboard.png)

---

## ✨ Features
- **🔍 Auto-Diagnosis:** Checks wireless interface states, rfkill hardware/software blocks, NetworkManager status, ping, and DNS resolution.
- **⚡ Interactive Repairs:**
  - Restart NetworkManager service.
  - Software-unblock all wireless devices (`rfkill unblock`).
  - Force start wireless adapters (brings up `wlan0` / `wlp`).
  - Repair DNS configuration (replaces DNS servers with `8.8.8.8` and `1.1.1.1` in `resolv.conf`).
  - Complete Network Reset (combines all repairs).

---

## 🚀 Step-by-Step Setup & Installation Guide

Follow these steps to download and run NeeWiFi:

### Step 1: Clone the Repository (Download karein)
Open your terminal and clone the repository:
```bash
git clone https://github.com/Neeshant01/nee-wifi-fixer.git
cd nee-wifi-fixer
```

### Step 2: Install UI Modules (Setup dependencies)
This tool requires the `rich` python module for rendering the diagnostic terminal interface:
```bash
pip install rich
```
> [!NOTE]
> Agar aapko system-wide block (`externally-managed-environment`) error aati hai, toh aap virtual environment setup kar sakte hain:
> ```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install rich
> ```

### Step 3: Run with Administrative Privileges (Sudo se chalayein)
Wireless card diagnosis and network manager repairs require root privileges. Run:
```bash
sudo python3 neewifi.py
```
*Virtual environment users can run using the virtual venv runtime:*
```bash
sudo ./venv/bin/python neewifi.py
```

---

## 📖 Complete Setup & Debugging Guide
For detailed configuration steps, network diagnostics, and fixing persistent DNS blocks, open the [SETUP_GUIDE.md](./SETUP_GUIDE.md).

---

## 🔧 Common Troubleshooting & Fixes

### 1. `PermissionError: [Errno 1] Operation not permitted`
Many commands (such as `rfkill` or modifying `resolv.conf`) require administrative privileges. Always run the script with `sudo`:
```bash
sudo python3 neewifi.py
```

### 2. `ModuleNotFoundError: No module named 'rich'`
Ensure you have installed the `rich` library inside the active Python environment:
```bash
pip install rich
```
If using a virtual environment, verify that you activated it (`source venv/bin/activate`) before launching the script.

---

## 📄 License
Distributed under the MIT License.
