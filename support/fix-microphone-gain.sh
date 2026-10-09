#!/bin/bash
set -euo pipefail
[[ ${1:-} == "" || ${1:-} == "--persist" ]] || { echo 'Usage: fix-microphone-gain.sh [--persist]' >&2; exit 1; }
[[ $(cat /sys/class/dmi/id/sys_vendor) == "ASUSTeK COMPUTER INC." ]] &&
  omarchy-hw-match '^ASUS Vivobook S 16 M5606UA_M5606UA$' || exit 1
for codec in /proc/asound/card*/codec*; do
  if grep -q '^Codec: Realtek ALC294$' "$codec" && grep -q '^Subsystem Id: 0x10433be0$' "$codec"; then
    cardnum=${codec#*/card}
    cardnum=${cardnum%%/*}
    amixer -c "$cardnum" set 'Internal Mic Boost' 0 >/dev/null
    if [[ ${1:-} == "--persist" ]]; then
      if [[ -t 0 ]]; then
        sudo alsactl store "$cardnum"
      else
        pkexec /usr/bin/alsactl store "$cardnum"
      fi
    fi
    printf 'Internal microphone boost is now 0 dB on card %s.\n' "$cardnum"
    exit 0
  fi
done
echo 'Verified ALC294 microphone not found; no changes made.' >&2
exit 1
