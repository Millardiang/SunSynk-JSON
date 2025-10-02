# ⚡ Sunsynk Data Fetcher

This project provides Python scripts for retrieving data from a **Sunsynk solar inverter** using the Sunsynk Cloud API.  
It can output results as JSON and plain text files, and optionally publish data to an MQTT broker.  

⚠️ **Note**: This code is only compatible with SunSynk inverters which use the **Region 2 API**.

---

## 📂 File Layout

```
sunsynk/
├── sunsynk_get.py       # One-time fetch script
├── sunsynk.py           # Continuous looping fetcher
├── options.json         # Configuration file
└── README.md            # Documentation
```

---

## 📜 Contents

- **sunsynk_get.py** – One-off data grab for manual use or cron jobs.  
- **sunsynk.py** – Continuous looping fetcher, outputs JSON/TXT, can publish via MQTT.  
- **options.json** – Stores API credentials, broker details, and polling settings.  

---

## 🛠 Requirements

- Python **3.9+**  
- Dependencies:
  - `requests`
  - `paho-mqtt`

Install requirements:
```bash
pip install requests paho-mqtt
```

---

## ⚙️ Configuration

All settings are stored in **`options.json`**. Example:

```json
{
  "API_Server": "api.sunsynk.net",
  "sunsynk_user": "your_username",
  "sunsynk_pass": "your_password",
  "inverter_serial": "your_inverter_serial_number",
  "mqtt_broker": "your_mqtt_broker_IP_address",
  "mqtt_port": 1883,
  "mqtt_topic": "sunsynk",
  "output_txt": "/tmp/sunsynk/sunsynk_text_dump.txt",
  "output_json": "/var/www/html/jsondata/sunsynk.json",
  "loop_time": 300,
  "options_file": "/var/www/html/jsondata/options.json"
}
```

🔑 **Key Fields**  
- **API_Server** – Sunsynk Cloud API endpoint.  
- **sunsynk_user / sunsynk_pass** – Login credentials.  
- **inverter_serial** – Serial number of your inverter.  
- **mqtt_broker / mqtt_port / mqtt_topic** – MQTT broker settings.  
- **output_txt / output_json** – Output file paths.  
- **loop_time** – Interval between API calls (for `sunsynk.py`).  
- **options_file** – Path to the JSON configuration file.  

---

## ▶️ Usage

### One-time Data Fetch
```bash
python3 sunsynk_get.py
```
✅ Fetches inverter data once → outputs JSON + TXT.

### Continuous Polling
```bash
python3 sunsynk.py
```
✅ Polls every `loop_time` seconds → updates files + publishes to MQTT.  

---

## 🚀 Installation

### 1. Place Files
```bash
sudo mkdir -p /opt/sunsynk
sudo cp sunsynk.py sunsynk_get.py options.json /opt/sunsynk/
```

### 2. Install Dependencies
```bash
pip install requests paho-mqtt
```

### 3. Test Manually
```bash
cd /opt/sunsynk
python3 sunsynk_get.py
python3 sunsynk.py
```

### 4. Create a Systemd Service
Create `/etc/systemd/system/sunsynk.service`:

```ini
[Unit]
Description=Sunsynk Data Fetcher Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/sunsynk/sunsynk.py
WorkingDirectory=/opt/sunsynk
Restart=always
RestartSec=10
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sunsynk.service
sudo systemctl start sunsynk.service
```

Check status/logs:
```bash
systemctl status sunsynk.service
journalctl -u sunsynk.service -f
```

---

## 🗺 Data Flow Map

```text
            +-------------------+
            |   options.json    |
            | (credentials, cfg)|
            +-------------------+
                      |
     ---------------------------------------
     |                                     |
+---------------+                 +----------------+
| sunsynk_get.py|   one-time fetch|   sunsynk.py   |  continuous loop
+---------------+                 +----------------+
     |                                     |
     v                                     v
+-------------------+              +-------------------+
| sunsynk_text_dump |              | sunsynk_text_dump |
|   (plain text)    |              |   (plain text)    |
+-------------------+              +-------------------+
     |                                     |
     v                                     v
+-------------------+              +-------------------+
|   sunsynk.json    |              |   sunsynk.json    |
|  (structured data)|              |  (structured data)|
+-------------------+              +-------------------+
                                           |
                                           v
                                 +-------------------+
                                 |    MQTT Broker    |
                                 | (optional publish)|
                                 +-------------------+
```

---

## 📤 Output

- **Text dump** – Key/value pairs (`output_txt`).  
- **JSON** – Structured inverter data (`output_json`).  
- **MQTT** – Published messages (if broker enabled).  

---

## ❗ Troubleshooting

- **Login fails** → Check username/password, ensure inverter is registered in Sunsynk Cloud.  
- **No data returned** → Verify `inverter_serial`.  
- **MQTT errors** → Check broker connection and firewall.  
- **Permission issues** → Ensure user can write to output paths.  
- **Rate limits** → Increase `loop_time` to avoid API blocks.  

---

## 📜 License

Copyright (C) 2025 Ian Millard  
Licensed under the GNU General Public License v3.0 (GPL-3.0).  
See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html).
