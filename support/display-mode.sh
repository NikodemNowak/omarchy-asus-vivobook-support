#!/bin/bash
set -euo pipefail
external_flag="$HOME/.local/state/omarchy/toggles/hypr/vivobook-external-disable.lua"
case "${1:-}" in
  internal)
    omarchy-hyprland-monitor-internal-mirror off
    omarchy-hyprland-monitor-internal on
    mkdir -p "$(dirname "$external_flag")"
    python3 - "$external_flag" <<'PYMODE'
import json,pathlib,re,subprocess,sys
outputs=json.loads(subprocess.check_output(['hyprctl','-j','monitors','all']))
names=[o['name'] for o in outputs if not re.match(r'^(eDP|LVDS|DSI)-',o['name'])]
if any(not re.fullmatch(r'[A-Za-z0-9._-]+',name) for name in names):
  raise SystemExit('Unsafe connector name')
pathlib.Path(sys.argv[1]).write_text(''.join('hl.monitor({ output = '+json.dumps(name)+', disabled = true })\n' for name in names))
PYMODE
    hyprctl reload >/dev/null
    ;;
  extend)
    rm -f "$external_flag"
    omarchy-hyprland-monitor-internal-mirror off
    omarchy-hyprland-monitor-internal on
    ;;
  mirror)
    rm -f "$external_flag"
    hyprctl reload >/dev/null
    omarchy-hyprland-monitor-internal-mirror on
    ;;
  external)
    omarchy-hw-external-monitors || { omarchy-osd -i display -m 'Podłącz drugi monitor'; exit 1; }
    rm -f "$external_flag"
    hyprctl reload >/dev/null
    omarchy-hyprland-monitor-internal-mirror off
    omarchy-hyprland-monitor-internal off
    ;;
  *) exit 1 ;;
esac
hyprctl reload >/dev/null
hyprctl configerrors
