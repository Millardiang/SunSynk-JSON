#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolarSynkV3 daemon — fetches inverter data via sunsynk_get functions,
writes log + JSON, publishes JSON to MQTT broker (retained),
and repeats every loop_time seconds (default 300).
Config is reloaded each cycle from options.json.

(c) 2025 Ian Millard
GNU GPL v3
"""

import os
import json
import traceback
import time
from datetime import datetime, timezone
from io import StringIO
import contextlib
import re
import ast

import paho.mqtt.client as mqtt  # safe classic import

from sunsynk_get import (
    gettoken,
    GetInverterInfo, GetPvData, GetGridData, GetBatteryData,
    GetLoadData, GetOutputData, GetDCACTemp, GetInverterSettingsData
)

# --- Helpers for cleaning + parsing ---

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def strip_ansi(text):
    return ansi_escape.sub('', text)

def to_camel_case(s: str) -> str:
    parts = re.split(r'[\s_/]+', s.strip())
    if not parts:
        return s
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

def normalise_key(key: str, section: str) -> str:
    prefixes = [
        "Inverter Setting ", "Inverter ",
        "PV ", "Grid ", "Battery ",
        "Load ", "Output "
    ]
    for p in prefixes:
        if key.startswith(p):
            key = key[len(p):]
            break
    key = to_camel_case(key)
    section_prefix = section[0].lower() + section[1:]
    return section_prefix + key[0].upper() + key[1:]

def capture_and_parse(func, section_name, *args):
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args)
    raw_output = buf.getvalue()
    clean_output = strip_ansi(raw_output)

    parsed = {}
    log_lines = []

    for line in clean_output.splitlines():
        log_lines.append(line)
        if ":" in line:
            k, v = line.split(":", 1)
            key = normalise_key(k.strip(), section_name)
            value = v.strip()

            if value.startswith("[") and value.endswith("]"):
                try:
                    value = ast.literal_eval(value)
                except Exception:
                    pass
            elif value.lower() in ("true", "false"):
                value = value.lower() == "true"
            elif value in ("None", "null"):
                value = None
            elif re.fullmatch(r"-?\d+", value):
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass

            parsed[key] = value

    return parsed, log_lines

# --- Main fetch run ---

def main(cfg):
    log_lines = []
    flat_all = {}

    try:
        serials_raw = cfg.get("inverter_serial") or cfg.get("sunsynk_serial") or "2212176166"
        serials = str(serials_raw).split(";")
        mqtt_broker = cfg.get("mqtt_broker", "192.168.1.150")
        mqtt_port = int(cfg.get("mqtt_port", 1883))
        mqtt_topic = cfg.get("mqtt_topic", "sunsynk")
        output_txt = cfg.get("output_txt", "sunsynk_text_dump.txt")
        output_json = cfg.get("output_json", "sunsynk_from_text.json")

        print("▶ Starting new Sunsynk fetch cycle...")
        print(f"Using serials: {serials}")
        print(f"MQTT: {mqtt_broker}:{mqtt_port}, topic={mqtt_topic}")
        print(f"Outputs: txt={output_txt}, json={output_json}")

        print("🔑 Getting token...")
        token = gettoken()
        print("✅ Got token")

        for serial in serials:
            if not serial.strip():
                continue
            print(f"=== Inverter {serial} ===")

            try:
                data, out = capture_and_parse(GetInverterInfo, "inverter", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetPvData, "pv", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetGridData, "grid", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetBatteryData, "battery", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetLoadData, "load", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetOutputData, "output", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetDCACTemp, "dcac", token, serial)
                flat_all.update(data)

                data, out = capture_and_parse(GetInverterSettingsData, "inverterSettings", token, serial)
                flat_all.update(data)

            except Exception as e:
                print(f"❌ Error while fetching data for {serial}: {e}")
                traceback.print_exc()

        wrapped = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **flat_all
        }

        # Ensure output dirs exist safely
        out_txt_dir = os.path.dirname(output_txt)
        if out_txt_dir:
            os.makedirs(out_txt_dir, exist_ok=True)

        out_json_dir = os.path.dirname(output_json)
        if out_json_dir:
            os.makedirs(out_json_dir, exist_ok=True)

        with open(output_txt, "w", encoding="utf-8") as lf:
            lf.write("\n".join(log_lines))
        print(f"💾 Wrote log to {output_txt}")

        with open(output_json, "w", encoding="utf-8") as jf:
            json.dump(wrapped, jf, indent=2)
        print(f"💾 Wrote JSON to {output_json}")

        try:
            client = mqtt.Client()
            client.connect(mqtt_broker, mqtt_port, 60)
            client.publish(mqtt_topic, json.dumps(wrapped), qos=0, retain=True)
            client.disconnect()
            print(f"📡 Published JSON to MQTT {mqtt_broker}:{mqtt_port}/{mqtt_topic}")
        except Exception as e:
            print(f"⚠️ MQTT publish failed: {e}")

    except Exception as e:
        print(f"❌ Fatal error in main(): {e}")
        traceback.print_exc()

# --- Daemon loop with config reload each cycle ---

if __name__ == "__main__":
    while True:
        try:
            config_file = "/var/www/html/divumwx/jsondata/options.json"
            if os.path.isfile(config_file):
                with open(config_file) as f:
                    cfg = json.load(f)
            else:
                cfg = {}

            loop_time = int(cfg.get("loop_time", 300))
            print(f"⏱ Loop interval set to {loop_time} seconds")

            main(cfg)
            print(f"✅ Cycle finished at {datetime.now(timezone.utc).isoformat()}")

        except Exception as e:
            print(f"⚠️ Error in main loop: {e}")

        time.sleep(loop_time)
