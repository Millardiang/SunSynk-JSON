# Sunsynk Data Fetcher

This project provides Python scripts for retrieving data from a **Sunsynk solar inverter** using the Sunsynk Cloud API.  
It can output results as JSON and plain text files, and optionally publish data to an MQTT broker. 

Please note that this code is only compatible with SunSynk inverters which use the Region 2 API.

---

## Contents

- **sunsynk_get.py**  
  Standalone script that authenticates with the Sunsynk API and fetches inverter data once.  
  Suitable for manual runs or cron jobs.

- **sunsynk.py**  
  A looping script/service that runs continuously, fetching inverter data at a defined interval.  
  Can write to JSON, text, and/or publish via MQTT.

- **options.json**  
  Configuration file containing API credentials, output paths, MQTT broker details, and polling interval.

---

## Requirements

- Python 3.9+  
- Dependencies:
  - `requests`
  - `paho-mqtt`

Install requirements:
```bash
pip install requests paho-mqtt
```

---

## Configuration

Settings are stored in **`options.json`**. Example:

```json
{
  "API_Server": "api.sunsynk.net",
  "sunsynk_user": "your_username",
  "sunsynk_pass": "your_password",
  "inverter_serial": "1234567890",
  "mqtt_broker": "127.0.0.1",
  "mqtt_port": 1883,
  "mqtt_topic": "sunsynk",
  "output_txt": "/tmp/sunsynk/sunsynk_text_dump.txt",
  "output_json": "/var/www/html/divumwx/jsondata/sunsynk.json",
  "loop_time": 300,
  "options_file": "/var/www/html/divumwx/jsondata/options.json"
}
```

### Key Fields
- **API_Server** – The Sunsynk Cloud API endpoint.  
- **sunsynk_user / sunsynk_pass** – Your login credentials.  
- **inverter_serial** – Serial number of your Sunsynk inverter.  
- **mqtt_broker / mqtt_port / mqtt_topic** – MQTT broker settings if you want to publish.  
- **output_txt / output_json** – File paths for plain text and JSON output.  
- **loop_time** – Interval in seconds between API calls (`sunsynk.py` only).  
- **options_file** – Path to the JSON configuration file.  

---

## Usage

### One-time Data Fetch
Run:
```bash
python3 sunsynk_get.py
```
- Fetches inverter data once.
- Writes to `output_txt` and `output_json`.

### Continuous Polling
Run:
```bash
python3 sunsynk.py
```
- Polls the inverter every `loop_time` seconds.
- Writes updated output files.
- Publishes to MQTT if configured.

---

## Output

- **Text dump**: Simple key/value pairs in a plain text file.  
- **JSON**: Structured inverter data for dashboards or downstream processing.  
- **MQTT**: Published messages under the configured topic.  

---

## Troubleshooting

- **Login fails**: Check your username/password and make sure your inverter is registered with the Sunsynk Cloud.  
- **No data returned**: Verify the `inverter_serial`.  
- **MQTT errors**: Ensure your broker is running and accessible.  
- **Permission issues**: Make sure your user can write to the output paths.  
- **Rate limits**: If you poll too often, the API may block requests. Increase `loop_time`.  

---

## License

Copyright (C) 2025 Ian Millard  
Licensed under the GNU General Public License v3.0 (GPL-3.0).  
See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html).
