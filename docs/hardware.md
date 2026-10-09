# Hardware and validation

Test platform: ASUS Vivobook S 16 M5606UA_M5606UA, BIOS M5606UA.316, Omarchy 4.0.4-1, kernel 7.2.5-3-omarchy. Tested on one machine. Other Vivobook models are not automatically supported.

| Function | Status | Evidence / remaining work |
| --- | --- | --- |
| Keyboard backlight | Tested | Kernel consumes F4; sysfs hardware events drive OSD 0/3–3/3. Repeated off/off/restore preserves level. |
| Volume and screen brightness | Existing bindings | Stock Omarchy controls; speakers confirmed audible by owner. |
| HDMI displays | Tested | ASUS XG27ACMS 2560x1440@120, laptop 120 Hz; internal, extend, mirror, external. |
| F7 projection | Owner confirmed menu opens | Physical raw event not conclusively captured; Super+P override replaces pseudo-window shortcut. |
| F8 emoji | Owner confirmed emoji UI | WMI 0x7e, KEY_BLUETOOTH, XF86Bluetooth. |
| F9 mic mute LED | Tested | WMI 0x7c KEY_MICMUTE; LED follows default PipeWire source mute. |
| F10 microphone modes | Module routing tested; acoustic test pending | WMI 0xcb KEY_F14, XKB code 192 (XF86Launch5); optional WebRTC echo cancellation, not vendor beamforming. |
| F12 MyASUS key | Owner confirmed menu | WMI 0x86 KEY_PROG1, XF86Launch1 opens local laptop menu. |
| Microphone capture | Owner uses dictation; first sample noisy, new speech test pending | ALC294 subsystem 1043:3be0. Initial clipping observed. No speculative codec verbs or gain fix applied. |
| Camera | Capture tested | UVC camera delivers frame; app controls/privacy key not yet tested. |
| Wi-Fi | Connected | MediaTek MT7922, mt7921e. Reconnect after suspend pending. |
| Bluetooth | Service enabled, controller powered | Pairing pending. |
| Touchpad | Detected | ASCF1201:00 2808:0231; full gestures still need user validation. |
| Power profiles | Tested | quiet/balanced/performance supported; balanced restored. |
| Charge limit | Kernel interface available | BAT1 charge_control_end_threshold; initially 100%. Menu exposes session-only 60/80/100% limits with graphical authorization; changing the limit has not yet been tested. |
| Suspend/resume | Pending | Kernel offers s2idle only. Must test keyboard, audio, network and display recovery. |
| USB-C/USB4 display | Pending | UCSI timeout seen in logs; no validated display failure or firmware change. |
| AMD NPU | Driver bound | amdxdna; application inference not tested. |
| Vendor microphone directionality / RGB effects | Unavailable / unverified | No equivalent vendor implementation included. |

No serial numbers, network addresses, microphone recordings or private desktop images are included.

## Upstream work

- Keyboard hardware OSD: https://github.com/omacom/omarchy/pull/14743 (draft; native QML runtime validation pending).
- Idle snapshot fix validation: https://github.com/omacom/omarchy/pull/10364#issuecomment-6083908111.
- Model-specific hotkey PR: being prepared separately.

## Manual acceptance steps

1. Set keyboard brightness to 2/3. Let idle blank it, wake by typing, then repeat. Expect 2/3 both times. Select 0/3 and verify waking does not light it.
2. Press F8/F10/F12 (with Fn if applicable), verify emoji/microphone/laptop menus. Toggle F9 and inspect its LED.
3. Select each F7 display mode with a monitor connected; restore extend. Unplug monitor from external-only mode and verify internal recovery.
4. Start a new call after selecting conference microphone mode. Compare echo with normal mode, then restore normal. Existing applications may retain their selected device.
5. Suspend briefly. On resume test network, playback, capture, both displays and keyboard brightness. Repeat after reboot.
6. Repeat display tests over USB-C and pair a Bluetooth device.
