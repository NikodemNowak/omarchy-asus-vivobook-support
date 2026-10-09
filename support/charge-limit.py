#!/usr/bin/env python3
"""Set the current-session ASUS battery charge limit with a graphical root prompt."""
from pathlib import Path
import subprocess
import sys

if len(sys.argv) != 2 or sys.argv[1] not in ('60', '80', '100'):
    raise SystemExit('Usage: charge-limit.py 60|80|100')
target = Path('/sys/class/power_supply/BAT1/charge_control_end_threshold')
if not target.exists():
    raise SystemExit('Battery charge limit is unavailable on this kernel.')
subprocess.run(['pkexec', '/usr/bin/tee', str(target)], input=sys.argv[1] + '\n', text=True,
               stdout=subprocess.DEVNULL, check=True)
if target.read_text().strip() != sys.argv[1]:
    raise SystemExit('The battery did not accept the requested threshold.')
