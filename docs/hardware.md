# Hardware and validation

Test platform: ASUS Vivobook S 16 M5606UA_M5606UA, BIOS M5606UA.316, Omarchy 4.0.4-1, kernel 7.2.5-3-omarchy. Tested on one machine. Other Vivobook models are not automatically supported.

| Function | Status | Evidence / remaining work |
| --- | --- | --- |
| Keyboard backlight | Tested | Kernel consumes F4; sysfs hardware events drive OSD 0/3–3/3. Repeated off/off/restore preserves level. |
| Volume and screen brightness | Existing bindings | Stock Omarchy controls; speakers confirmed audible by owner. |
| HDMI displays | Tested | ASUS XG27ACMS 2560x1440@120, laptop 120 Hz; internal, extend, mirror, external. |
| F7 projection | Owner confirmed menu opens | Physical raw event not conclusively captured; Super+P override replaces pseudo-window shortcut. |
| F8 emoji | Owner confirmed emoji UI | WMI 0x7e defaults to KEY_BLUETOOTH and toggles rfkill. A model-specific hwdb remaps it to KEY_PROG2 / XF86Launch2; owner confirmed emoji still opens while Bluetooth stays on. |
| F9 mic mute LED | Tested | WMI 0x7c KEY_MICMUTE; LED follows default PipeWire source mute. |
| F10 microphone modes | Owner confirmed F10; module routing tested; acoustic test pending | WMI 0xcb KEY_F14, XKB code 192 (XF86Launch5); optional WebRTC echo cancellation, not vendor beamforming. |
| F12 MyASUS key | Owner confirmed menu | WMI 0x86 KEY_PROG1, XF86Launch1 opens local laptop menu. |
| Microphone capture | Speech verified after removing +30 dB boost; startup transient remains | ALC294 subsystem 1043:3be0. Default +30 dB boost caused 17–63% clipped samples after startup. With boost 0, speech clips 0% from second 2 onward; owner confirms clear voice. First-second startup transient remains. No codec verbs applied. |
| Camera | Capture tested | UVC camera delivers frame; app controls/privacy key not yet tested. |
| Wi-Fi | Connected | MediaTek MT7922, mt7921e. Reconnect after suspend pending. |
| Bluetooth | Bose paired and AAC playback heard by owner | Manual reconnect failed with le-connection-abort-by-local; further reconnect validation pending. |
| Touchpad | Detected | ASCF1201:00 2808:0231; full gestures still need user validation. |
| Power profiles | Tested | quiet/balanced/performance supported; balanced restored. |
| Charge limit | Kernel interface available | BAT1 charge_control_end_threshold; initially 100%. Menu exposes session-only 60/80/100% limits with graphical authorization; setting 80% and restoring 100% was validated. |
| Suspend/resume | One actual s2idle cycle passed basic checks | Network connected, keyboard lit, both direct-HDMI displays recovered at 120 Hz, mic gain remained 0 dB, camera captured after resume. Audio acceptance after resume still needs owner confirmation. |
| USB-C hub display | Reproduced failure on both ports | Owner reports iSpot 8-in-1 item 46036 hub. DP-1/DP-2 detects monitor and EDID, but width/height remain 0; DRM atomic TEST_ONLY returns EINVAL even in low-bandwidth modes. Root cause not established. UCSI -110 after resume. Charging through hub not validated; battery reported discharging. |
| AMD NPU | Driver bound | amdxdna; application inference not tested. |
| Vendor microphone directionality / RGB effects | Unavailable / unverified | No equivalent vendor implementation included. |

No serial numbers, network addresses, microphone recordings or private desktop images are included.

## Upstream work

- Keyboard hardware OSD: https://github.com/omacom/omarchy/pull/14743 (draft; native QML runtime validation pending).
- Idle snapshot fix validation: https://github.com/omacom/omarchy/pull/10364#issuecomment-6083908111.
- Microphone gain fix: https://github.com/omacom/omarchy/pull/14747 (draft; reboot validation pending).
- Model-specific hotkeys: https://github.com/omacom/omarchy/pull/14746 (draft; owner confirmed all mapped keys).

## Manual acceptance steps

1. Set keyboard brightness to 2/3. Let idle blank it, wake by typing, then repeat. Expect 2/3 both times. Select 0/3 and verify waking does not light it.
2. Press F8/F10/F12 (with Fn if applicable), verify emoji/microphone/laptop menus. Toggle F9 and inspect its LED.
3. Select each F7 display mode with a monitor connected; restore extend. Unplug monitor from external-only mode and verify internal recovery.
4. Start a new call after selecting conference microphone mode. Compare echo with normal mode, then restore normal. Existing applications may retain their selected device.
5. Suspend briefly. On resume test network, playback, capture, both displays and keyboard brightness. Repeat after reboot.
6. Repeat display tests over USB-C and pair a Bluetooth device.
