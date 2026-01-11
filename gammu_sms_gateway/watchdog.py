#!/usr/bin/env python3
import sys
import json
import time
import subprocess
from pathlib import Path

OPTIONS_PATH = Path("/data/options.json")

def load_options():
    with open(OPTIONS_PATH, "r") as f:
        return json.load(f)

def send_sms(number: str, text: str):
    subprocess.call(["gammu-smsd-inject", "TEXT", number, "-text", text])

def can_ping(host: str) -> bool:
    try:
        # ping -c 1 -W 2 HOST
        res = subprocess.call(["ping", "-c", "1", "-W", "2", host])
        return res == 0
    except Exception:
        return False

def main():
    if len(sys.argv) < 3:
        sys.exit(0)

    interval = int(sys.argv[1])
    host = sys.argv[2]

    opts = load_options()
    primary = opts.get("primary_number")
    if not primary:
        sys.exit(0)

    in_emergency = False

    while True:
        ok = can_ping(host)

        if ok and in_emergency:
            # návrat do normálu
            send_sms(primary, "Internet obnoven. Vracim se k beznym notifikacim.")
            in_emergency = False

        if not ok and not in_emergency:
            # přechod do nouzového režimu
            send_sms(primary, "Nouzovy rezim aktivni: internet nedostupny, prepinam na SMS.")
            in_emergency = True

        time.sleep(interval)

if __name__ == "__main__":
    main()
