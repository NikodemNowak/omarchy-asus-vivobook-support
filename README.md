# Omarchy support for ASUS Vivobook S 16 M5606UA

A reproducible configuration for the tested M5606UA laptop. Work in progress: this is not a claim that every hardware feature works. See the [hardware matrix and test procedure](docs/hardware.md).

Includes keyboard backlight persistence and 0/3–3/3 OSD, special-key mappings, a four-mode projection menu, microphone mute LED synchronization, optional PipeWire WebRTC conference audio, and a laptop controls menu with session-only battery charge limits (60/80/100%).

## Install

Run inside your Omarchy desktop session:

```sh
sudo ./setup-hotkeys.sh
python3 install.py
```

The root setup remaps the emoji key to a non-radio key, preventing F8 from disabling Bluetooth. The desktop installer checks the exact DMI model, merges menu entries, preserves unrelated user configuration, backs up changed files, and enables two user services. It does not write packaged Omarchy files or change firmware, kernel parameters, mixer gain, Bluetooth system service or your monitor resolution. Super+P is reassigned from pseudo-window toggle to the projection menu.

For a preview without writes:

```sh
python3 install.py --dry-run
```

To remove an installation made with this installer:

```sh
python3 install.py --uninstall
```

To remove the system keymap as well, run `sudo ./setup-hotkeys.sh --uninstall` and reboot. Uninstall checks for subsequent edits before restoring backups. Manual configuration from before this installer is preserved as the baseline.

## Microphone

F10 offers normal capture and an optional conversation mode with PipeWire/WebRTC echo cancellation. Select the mode before starting a call. The processed source and playback sink are paired; return to normal to restore previous default devices. The mode lasts for the current audio session. ASUS proprietary directional microphone modes are not implemented. No audio is uploaded.

For the verified ALC294 speech-clipping fix, run:

```sh
./support/fix-microphone-gain.sh --persist
```

This removes the extra +30 dB internal microphone boost and stores ALSA state (requires authentication). It leaves Capture and headset boost untouched. On our machine the corresponding input slider becomes about 32%; raising it back to 100% can restore the excessive hardware boost. A separate first-second startup transient remains under investigation.

## Display tuning

Monitor model and refresh rate are user choices and are not enforced by installation. Our HDMI test used an ASUS XG27ACMS at 2560x1440@120. Configure a supported mode in your own `~/.config/hypr/monitors.lua`.

## Upstream

The generic keyboard OSD implementation is submitted separately in [Omarchy PR #14743](https://github.com/omacom/omarchy/pull/14743). Other changes are tracked independently so maintainers can review each behavior.

Omarchy-derived wrapper scripts retain the upstream MIT license. This repository is intended as a transparent testbed while upstream contributions are reviewed.
