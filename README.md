# ESP32 Marauder Web Serial Console 🌐⚡

This project is a **Web-based Serial Console** for controlling the **ESP32 Marauder firmware** from your browser.  
It works on **Windows, Linux (Debian/Ubuntu), MacOS, and WSL** using the Web Serial API.

---

## ✅ Features
- Cross-platform Web Serial console
- Beautiful responsive UI (HTML + CSS only)
- Shows all ESP32 Marauder command outputs clearly
- Auto-detects COM ports / serial ports
- Fully works in your browser with no complex setup

---

## 🔌 Hardware Requirements
- ESP32-WROOM-32 (or any ESP32 running Marauder firmware)
- MicroSD Card (optional)
- CP2102/CP210x USB-to-Serial driver (for Windows/Mac)

---

## ⚙️ Software Setup

### 1. 🔑 Install CP210x Drivers

- Download: [CP210x USB to UART Bridge VCP Drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
- Install according to your OS (Windows, MacOS, Linux).

On Windows, after installation, you’ll see your ESP32 as **COM3, COM4, etc.**
On Linux/MacOS, it will appear as `/dev/ttyUSB0`, `/dev/tty.SLAB_USBtoUART`, etc.

---

### 2. 🐍 Install Python (If not already installed)

Open CMD or Terminal:
```bash
python --version



If not found, install Python 3 from: https://www.python.org/downloads/
Then verify:

python3 --version

git clone https://github.com/pulkit6732/ESP32_marunder.git


# On Windows / Linux / MacOS / WSL:
python3 -m http.server 8080

on windows open the file which contain the git files then open cmd by right click and write  
python -m http.server 8080

open chrome browser type 
http://localhost:8080

Click "Connect"

Select your ESP32 port (e.g., COM3, /dev/ttyUSB0, etc.)

Set Baud Rate to 115200

Hit "Connect"

Start typing commands in the input box!


📖 Full command list:
➡️ https://github.com/justcallmekoko/ESP32Marauder/wiki/attack

📖 Deauth Attack Example:
➡️ https://github.com/justcallmekoko/ESP32Marauder/wiki/deauthentication-attack-workflow

Example commands:
help             # List all commands
scan             # Start WiFi scan
deauth -t <target MAC> -b <BSSID>  # Start deauth attack
ble_scan         # Scan for BLE devices



![Screenshot 2025-07-06 184306](https://github.com/user-attachments/assets/c80cceae-3845-4c12-b593-19952680ff4a)


TROUBLESHOOT 
| Problem                          | Solution                                        |
| -------------------------------- | ----------------------------------------------- |
| Port not detected                | Install CP210x drivers correctly                |
| Access denied to serial port     | Close any other app using the COM port          |
| Broken command output formatting | Make sure you're using the latest UI files here |
| Python not recognized            | Add Python to your PATH during installation     |



 Credits
ESP32 Marauder: https://github.com/justcallmekoko/ESP32Marauder

Original inspiration from TechChip and community projects.


 Tested On:
Windows 10 Pro / Home

Windows 11 Pro / Home

Kali Linux, Ubuntu, Debian

MacOS Ventura, Sonoma

WSL2 (Ubuntu)


