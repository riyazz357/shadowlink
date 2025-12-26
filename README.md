# 🕵️‍♂️ Project ShadowLink: Level 2 RAT (Remote Access Tool)

**Project ShadowLink** is an advanced Python-based Reverse Shell implementation designed for Red Team operations and cybersecurity education.

Unlike basic netcat listeners, ShadowLink features a custom Application Layer protocol to handle **stateful directory navigation** and **reliable binary file transfer** (Upload/Download) over raw TCP sockets.

---

## ⚠️ Legal Disclaimer
**FOR EDUCATIONAL PURPOSES ONLY.**
This software is developed for authorized security testing and educational simulations.
* Do not install this payload on systems you do not own or have explicit permission to test.
* Unauthorized access to computer systems is illegal and punishable by law.
* The developers assume no liability for misuse.

---

## 🚀 Key Features

* **🔥 Reverse TCP Connection:** Bypasses inbound firewall rules by initiating the connection from the client side.
* **📂 Stateful Navigation:** Custom implementation of `cd` allows persistent directory changes (unlike standard `subprocess` calls).
* **💾 Data Exfiltration (Download):** Reliable extraction of files (text, images, binaries) from the target machine.
* **📦 Payload Delivery (Upload):** Ability to push new tools or files from the C2 server to the target.
* **👻 Stealth Mode:** Compatible with `PyInstaller` for "No-Console" background execution.

---

## 🛠️ Architecture

The project consists of two core components:

1.  **The Commander (`server.py`):**
    * Listens on a specified port.
    * Parses user input for special keywords (`upload`, `download`, `cd`).
    * Manages the handshake protocol for file transfers.

2.  **The Agent (`client.py`):**
    * Connects back to the Commander.
    * Executes system commands via `subprocess`.
    * Handles file streams and acknowledges receipt/delivery of data.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
* Python 3.x
* `pip` (Python Package Manager)

### 2. Configuration
Open `client.py` and configure the connection details:

```python
# client.py

# For Local LAN testing (Recommended):
ATTACKER_IP = "192.168.1.X"  # Replace with your Server's Local IP
PORT = 4444

# For WAN (Over Internet):
# ATTACKER_IP = "0.tcp.ngrok.io"
# PORT = 12345
