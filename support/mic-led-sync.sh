#!/bin/bash
set -uo pipefail
sync_led() {
  local state
  state=$(wpctl get-volume @DEFAULT_AUDIO_SOURCE@ 2>/dev/null) || return 0
  if [[ $state == *MUTED* ]]; then
    omarchy-brightness-keyboard-mute on
  else
    omarchy-brightness-keyboard-mute off
  fi
}
sync_led
pactl subscribe | while IFS= read -r event; do
  if [[ $event == *"on source #"* || $event == *"on server"* ]]; then
    sync_led
  fi
done
