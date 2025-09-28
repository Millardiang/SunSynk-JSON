#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolarSynkV3 daemon — fetches inverter data via sunsynk_get functions,
writes log to sunsynk_text_dump.txt,
writes structured flat JSON to sunsynk_from_text.json,
publishes JSON to MQTT broker,
and repeats every 300 seconds.

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

import paho.mqtt.client as mqtt

from sunsynk_get import (
    gettoken,
    GetInverterInfo, GetPvData, GetGridData, GetBatteryData,
    GetLoadData, GetOutputData, GetDCACTemp, GetInverterSettingsData
)

# --- Helpers for cleaning + parsing ---

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def strip_ansi(text):
    """Remove ANSI escape codes (colours, bold, etc.)."""
    return ansi_escape.sub('', text)

def to_camel_case(s: str) -> str:
    """Convert string to camelCase."""
    parts = re.split(r'[\s_/]+', s.strip())
    if not parts:
        return s
    return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

def normalise_key(key: str, section: str) -> str:
    """Normalise key, camelCase, prefix with section."""
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
    """
    Run a sunsynk_get function that prints output.
    Capture prints, strip ANSI codes, parse into a flat dict.
    """
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        func(*args)  # call original function
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

            # Try list parsing
            if value.startswith("[") and value.endswith("]"):
                try:
                    value = ast.literal_eval(value)
                except Exception:
                    pass
            # Booleans
            elif value.lower() in ("true", "false"):
                value = value.lower() == "true"
            # None/null
            elif value in ("None", "null"):
                value = None
            # Int
            elif re.fullmatch(r"-?\d+", value):
                value = int(value)
            # Float
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass  # leave as string

            parsed[key] = value

    return parsed, log_lines

# --- Main fetch run ---

def main():
    log_lines = []
    flat_all = {}

    try:
        config_file = "./data/options.json"
        serials = []

        if os.path.isfile(config_file):
            with open(config_file) as f:
                cfg = json.load(f)
            serials_raw = cfg.get("inverter_serial") or cfg.get("sunsynk_serial") or ""
            serials = str(serials_raw).split(";")
            log_lines.append(f"Loaded serials: {serials}")
        else:
            serials = ["2212176166"]
            log_lines.append("Using fallback serials: ['2212176166']")

        log_lines.append("🔑 Getting token...")
        token = gettoken()
        log_lines.append("✅ Got token")

        for serial in serials:
            if not serial.strip():
                continue
            log_lines.append(f"\n=== Inverter {serial} ===")

            try:
                data, out = capture_and_parse(GetInverterInfo, "inverter", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetPvData, "pv", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetGridData, "grid", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetBatteryData, "battery", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetLoadData, "load", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetOutputData, "output", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetDCACTemp, "dcac", token, serial)
                flat_all.update(data); log_lines.extend(out)

                data, out = capture_and_parse(GetInverterSettingsData, "inverterSettings", token, serial)
                flat_all.update(data); log_lines.extend(out)

            except Exception as e:
                err = f"❌ Error while fetching data for {serial}: {e}"
                log_lines.append(err)
                traceback.print_exc()

        wrapped = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **flat_all
        }

        # Write fresh outputs each cycle
        with open("sunsynk_text_dump.txt", "w", encoding="utf-8") as lf:
            lf.write("\n".join(log_lines))

        with open("sunsynk_from_text.json", "w", encoding="utf-8") as jf:
            json.dump(wrapped, jf, indent=2)

        # --- Publish to MQTT broker ---
        try:
            client = mqtt.Client()
            client.connect("192.168.1.150", 1883, 60)
            client.publish("sunsynk", json.dumps(wrapped), qos=0, retain=True)
            client.disconnect()
            log_lines.append("✅ Published JSON to MQTT topic 'sunsynk' (retained)")
        except Exception as e:
            log_lines.append(f"⚠️ MQTT publish failed: {e}")

    except Exception as e:
        log_lines.append(f"❌ Fatal error in main(): {e}")
        traceback.print_exc()

# --- Daemon loop every 300 seconds ---

if __name__ == "__main__":
    while True:
        try:
            main()
            print(f"Run completed at {datetime.now(timezone.utc).isoformat()}")
        except Exception as e:
            print(f"⚠️ Error in main loop: {e}")
        time.sleep(300)
