#!/bin/bash
set -euo pipefail
(( EUID == 0 )) || { echo 'Run with sudo from your terminal.' >&2; exit 1; }
[[ $(cat /sys/class/dmi/id/sys_vendor) == "ASUSTeK COMPUTER INC." ]]
[[ $(cat /sys/class/dmi/id/product_name) == "ASUS Vivobook S 16 M5606UA_M5606UA" ]]
root_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
target=/etc/udev/hwdb.d/90-asus-vivobook-m5606-keyboard.hwdb
case "${1:-}" in
  "")
    if [[ -e $target ]] && ! cmp -s "$root_dir/config/emoji-key.hwdb" "$target"; then
      echo 'An existing custom mapping is present; preserve and reconcile it first.' >&2
      exit 1
    fi
    install -Dm644 "$root_dir/config/emoji-key.hwdb" "$target"
    systemd-hwdb update
    for event in /sys/class/input/event*; do
      if [[ $(cat "$event/device/name" 2>/dev/null) == "Asus WMI hotkeys" ]]; then
        udevadm trigger --action=change "$event"
      fi
    done
    udevadm settle
    ;;
  --uninstall)
    cmp -s "$root_dir/config/emoji-key.hwdb" "$target" || { echo 'Mapping changed; refusing removal.' >&2; exit 1; }
    rm "$target"
    systemd-hwdb update
    echo 'Reboot to restore the original kernel keymap.'
    ;;
  *) echo 'Usage: setup-hotkeys.sh [--uninstall]' >&2; exit 1 ;;
esac
