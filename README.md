# WeeWX Sunsynk Extension

A WeeWX 5.1 extension that integrates with **Sunsynk solar inverters**, pulling live data from the Sunsynk Cloud API and publishing it into:

- Local JSON and text files (for dashboards such as [DivumWX](https://claydonsweather.org.uk))  
- MQTT topics (for integration with Home Assistant, Node-RED, or other consumers)  
- WeeWX reporting loop (for archive/loop services)

---

## Contents

- `sunsynk_get.py`  
  Standalone utility for authenticating with the Sunsynk API and fetching inverter data.  
  Useful for testing, cron jobs, or debugging.

- `sunsynk.py`  
  WeeWX 5.1 **service** that integrates with the WeeWX engine.  
  Runs on the configured loop interval and publishes inverter data.

- `options.json`  
  JSON configuration file with API credentials, MQTT broker settings, and file output paths.

---

## Requirements

- **WeeWX 5.1+**  
- **Python 3.9+**  
- Python dependencies:
  - `requests`
  - `paho-mqtt`

Install requirements:
```bash
pip3 install requests paho-mqtt
```

---

## Installation

### Manual Install

1. Copy the files into your WeeWX installation:
   ```bash
   cp sunsynk.py /home/weewx/bin/user/
   cp sunsynk_get.py /home/weewx/bin/user/
   cp options.json /home/weewx/etc/
   ```

2. Edit `options.json` with your credentials and paths.

3. Edit `weewx.conf` and enable the service:

   ```ini
   [Engine]
     [[Services]]
       data_services = ..., user.sunsynk.Sunsynk
   ```

4. Restart WeeWX:
   ```bash
   sudo systemctl restart weewx
   ```

---

### Packaging with `weectl`

To package as a `.zip` extension:

1. Ensure you have:
   - `install.py`  
   - `bin/user/sunsynk.py`  
   - `bin/user/sunsynk_get.py`  
   - `skins/Sunsynk/options.json` (or your desired path)

2. Create the extension archive:
   ```bash
   zip -r weewx-sunsynk.zip install.py bin/ skins/
   ```

3. Install with:
   ```bash
   weectl extension install weewx-sunsynk.zip
   ```

---

## Configuration

All runtime settings are in **`options.json`**. Example:

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

---

## Usage

### Standalone Script

Run directly:
```bash
python3 sunsynk_get.py
```

- Fetches inverter data once.  
- Writes to the JSON/TXT paths defined in `options.json`.  
- Exits after one run.

### WeeWX Service

When enabled in `weewx.conf`, the `Sunsynk` service will:

- Poll the Sunsynk API every `loop_time` seconds.  
- Publish results into:
  - JSON output file
  - Text dump file
  - MQTT broker (if configured)

---

## Output

- **Text dump** (`output_txt`): Plain text with inverter metrics.  
- **JSON** (`output_json`): Full structured inverter data.  
- **MQTT**: Published messages under `mqtt_topic`.

---

## Troubleshooting

- **No token in login response**:  
  Check `sunsynk_user` / `sunsynk_pass` are correct.  
  Ensure the inverter is linked to your account in Sunsynk Cloud.

- **MQTT connection refused**:  
  Verify `mqtt_broker`, `mqtt_port`, and network connectivity.

- **File permission errors**:  
  Ensure the WeeWX user (`weewx:weewx`) has write access to `output_txt` and `output_json` directories.

- **Rate limits**:  
  Sunsynk Cloud API may block too-frequent requests. Increase `loop_time`.

---

## License

Copyright (C) 2025 Ian Millard  
Licensed under the GNU General Public License v3.0 (GPL-3.0).  

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html) for details.
