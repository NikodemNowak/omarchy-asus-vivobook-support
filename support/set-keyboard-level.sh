#!/bin/bash
set -euo pipefail
[[ ${1:-} =~ ^[0-3]$ ]] || exit 1
exec {lock_fd}>"$XDG_RUNTIME_DIR/omarchy-brightness-keyboard-asus::kbd_backlight.lock"
flock "$lock_fd"
brightnessctl -d asus::kbd_backlight set "$1" >/dev/null
brightnessctl -sd asus::kbd_backlight >/dev/null
rm -f "$XDG_RUNTIME_DIR/omarchy-brightness-keyboard-asus::kbd_backlight.blanked"
"$HOME/.local/share/asus-vivobook-support/bin/omarchy-osd" -i keyboard -p "$(( $1 * 100 / 3 ))" --progress-text "$1/3"
