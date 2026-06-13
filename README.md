# NeeWiFi: Linux WiFi Troubleshooter & Fixer 📡🛠️

**NeeWiFi** is a lightweight, interactive terminal utility designed to diagnose and repair common wireless network issues in Linux (such as Kali Linux, Ubuntu, Debian).

If your WiFi is soft-blocked by the OS, disabled in software, NetworkManager has frozen, or you can connect to WiFi but cannot browse the web (DNS issues), **NeeWiFi** will automatically detect and fix the problem.

---

## ✨ Features
- **🔍 Auto-Diagnosis**: Scans your wireless interfaces, NetworkManager state, rfkill blocks, internet ping, and DNS resolution to identify exactly where the connection fails.
- **⚡ Interactive Repairs**:
  - **Option 1**: Restart NetworkManager service.
  - **Option 2**: Software-unblock all wireless devices (`rfkill unblock`).
  - **Option 3**: Force start wireless adapters (brings up `wlan0` / `wlp`).
  - **Option 4**: Repair DNS configuration (sets resolv.conf to public servers `8.8.8.8` and `1.1.1.1`).
  - **Option 5**: Complete Network Reset (combines all repairs in one click).

---

## 🚀 How to Run

Since network configurations require administrative changes, you **must run the script using sudo/root privileges**:

```bash
sudo python3 neewifi.py
```

### Dependencies
This script uses the `rich` library for rendering the CLI interface. If you run it outside your project's virtual environment, ensure you install it:
```bash
pip install rich
```
*Note: If you get an `externally-managed-environment` error, run the script from within your active Python virtual environment (`venv`) using `sudo ./venv/bin/python neewifi.py`.*

---

## 📄 License
Distributed under the MIT License.
