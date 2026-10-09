#!/usr/bin/python3
"""Show ASUS firmware keyboard brightness events without changing brightness."""
import fcntl, json, os, pathlib, select, subprocess
led = pathlib.Path('/sys/class/leds/asus::kbd_backlight')
runtime = pathlib.Path(os.environ['XDG_RUNTIME_DIR'])
maximum = int((led / 'max_brightness').read_text())
fd = os.open(led / 'brightness_hw_changed', os.O_RDONLY | os.O_NONBLOCK)
def acknowledge():
  os.lseek(fd, 0, os.SEEK_SET)
  return os.read(fd, 64)
acknowledge()
poll = select.poll()
poll.register(fd, select.POLLPRI | select.POLLERR)
lock = open(runtime / 'omarchy-brightness-keyboard-asus::kbd_backlight.lock', 'a')
while True:
  poll.poll()
  acknowledge()
  # The kernel handles F4 itself; changing the brightness again would double-step.
  fcntl.flock(lock, fcntl.LOCK_EX)
  try:
    value = int((led / 'brightness').read_text())
    result = subprocess.run(['brightnessctl', '-sd', 'asus::kbd_backlight'], stdout=subprocess.DEVNULL)
    if result.returncode == 0:
      (runtime / 'omarchy-brightness-keyboard-asus::kbd_backlight.blanked').unlink(missing_ok=True)
  finally:
    fcntl.flock(lock, fcntl.LOCK_UN)
  payload = json.dumps(dict(icon='keyboard', message='', value=str(value), max=str(maximum), progressText=f'{value}/{maximum}', duration='1400'))
  subprocess.run(['omarchy-shell', '-q', 'osd', 'show', payload], check=False)
