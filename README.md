# 💡 Govee Smart Bulb Controller

A simple project to control **Govee Smart Bulbs** using Python over Bluetooth Low Energy (BLE). This project is intended for learning and experimentation with smart home device automation.

---

## 🚀 Features

- Power on/off the Govee bulb
- Change color using RGB values
- BLE-based communication (no cloud API required)
- CLI or script-based control

---

## 🔧 Requirements

- Python 3.7+
- A compatible BLE adapter (e.g., built-in BLE on Raspberry Pi)
- Govee BLE-capable smart bulb (tested on model H6001 / H6085 / etc.)
- To work with Smart Bulb create our own python virtual environment

  ```bash
  python3 -m venv smart_bulb
  source smart_bulb/bin/activate

### 🛠 Python Packages/Libraries

Install dependencies using:

```bash
pip install dbus-python - For IPC Communication
pip install bleak - For Authentication Mechanism
