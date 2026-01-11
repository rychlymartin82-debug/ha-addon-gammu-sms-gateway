#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path

OPTIONS_PATH = Path("/data/options.json")

def load_options():
    with open(OPTIONS_PATH, "r") as f:
        return json.load(f)

def is_allowed_number(number: str, allowed_numbers: list[str]) -> bool:
    return number in allowed_numbers

def send_confirmation(text: str):
    # Jednoduché potvrzení – později můžeme rozšířit
    opts = load_options()
    primary = opts.get("primary_number")
    if not primary:
        return
    subprocess.call(["gammu-smsd-inject", "TEXT", primary, "-text", text])

def main():
    # Gammu smsd runonreceive předává parametry:
    # 1: path to SMS file
    if len(sys.argv) < 2:
        sys.exit(0)

    sms_file = Path(sys.argv[1])

    # Parsování SMS souboru (jednoduchý způsob – podle formátu gammu)
    content = sms_file.read_text(errors="ignore")

    # Velmi jednoduchý parser: hledáme From: a Text:
    sender = ""
    text = ""

    for line in content.splitlines():
        if line.startswith("From:"):
            sender = line.split(":", 1)[1].strip()
        if line.startswith("Text:"):
            text = line.split(":", 1)[1].strip()

    opts = load_options()
    allowed_numbers = opts.get("allowed_numbers", [])
    restart_cmd = opts.get("restart_command", "restart")
    reboot_cmd = opts.get("reboot_command", "sms#reboot")

    if not is_allowed_number(sender, allowed_numbers):
        # Neautorizované číslo – ignorujeme
        sys.exit(0)

    if text == restart_cmd:
        # Restart HA Core
        subprocess.call(["ha", "core", "restart"])
        send_confirmation("Home Assistant byl restartovan.")
    elif text == reboot_cmd:
        # Restart celého hosta (HA Green)
        subprocess.call(["ha", "host", "reboot"])
        # potvrzení už nemusí odejít, zařízení padá :-)
    else:
        # Neznámý příkaz – nic
        pass

if __name__ == "__main__":
    main()
