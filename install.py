#!/usr/bin/env python3
"""Install local configuration with backups and guarded uninstall."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SERVICES = ['vivobook-keyboard-osd.service', 'vivobook-mic-led.service']


def command(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def plan(home):
    changes = {}
    support = Path('.local/share/asus-vivobook-support')
    for source in (ROOT / 'support').rglob('*'):
        if source.is_file() and '__pycache__' not in source.parts:
            changes[support / source.relative_to(ROOT / 'support')] = (source.read_bytes(), source.stat().st_mode & 0o777)
    changes[Path('.config/hypr/vivobook.lua')] = ((ROOT / 'config/vivobook.lua').read_bytes(), 0o644)
    for source in (ROOT / 'services').glob('*.service'):
        changes[Path('.config/systemd/user') / source.name] = (source.read_bytes(), 0o644)
    main = Path('.config/hypr/hyprland.lua')
    text = (home / main).read_text()
    if not re.search(r'^\s*require\(["\']hypr\.vivobook["\']\)', text, re.M):
        text += '\n-- ASUS Vivobook user configuration.\nrequire("hypr.vivobook")\n'
    changes[main] = (text.encode(), (home / main).stat().st_mode & 0o777)
    menu = Path('.config/omarchy/extensions/omarchy-menu.jsonc')
    existing = (home / menu).read_text() if (home / menu).exists() else '{}'
    stripped = re.sub(r'^\s*//.*$', '', existing, flags=re.M)
    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
    data = json.loads(stripped)
    data.update(json.loads((ROOT / 'config/menu.json').read_text()))
    changes[menu] = (json.dumps(data, ensure_ascii=False, indent=2).encode() + b'\n', 0o644)
    return changes


def install(home, dry_run=False):
    manifest = home / '.local/state/asus-vivobook-support/install.json'
    if manifest.exists():
        raise SystemExit('Already installed with this installer. Uninstall before reinstalling.')
    changes = plan(home)
    records = []
    for relative, (data, mode) in changes.items():
        target = home / relative
        if target.is_symlink():
            raise SystemExit(f'Refusing to replace symlink: {target}')
        previous = target.read_bytes() if target.exists() else None
        records.append(dict(path=str(relative), previous=base64.b64encode(previous).decode() if previous is not None else None,
                            mode=target.stat().st_mode & 0o777 if target.exists() else None, installed=digest(data)))
        print(target)
    if dry_run:
        return
    service_states = {}
    for name in SERVICES:
        service_states[name] = {key: subprocess.run(['systemctl', '--user', action, name], capture_output=True).returncode == 0
                               for key, action in [('enabled', 'is-enabled'), ('active', 'is-active')]}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(dict(files=records, services=service_states), indent=2))
    manifest.chmod(0o600)
    try:
        for relative, (data, mode) in changes.items():
            target = home / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
        validate()
        command('systemctl', '--user', 'daemon-reload')
        for name in SERVICES:
            command('systemctl', '--user', 'enable', '--now', name)
            command('systemctl', '--user', 'restart', name)
    except Exception:
        restore(home, manifest, guard=False)
        raise


def validate():
    command('hyprctl', 'reload')
    errors = command('hyprctl', 'configerrors')
    if errors:
        raise RuntimeError('Hyprland configuration errors: ' + errors)
    command('omarchy', 'menu', 'refresh')


def restore(home, manifest, guard=True):
    data = json.loads(manifest.read_text())
    if guard:
        changed = [item['path'] for item in data['files']
                   if not (home / item['path']).is_file() or (home / item['path']).is_symlink()
                   or digest((home / item['path']).read_bytes()) != item['installed']]
        if changed:
            raise SystemExit('Files changed since installation; preserve or reconcile them before uninstall:\n' + '\n'.join(changed))
    for name, previous in data['services'].items():
        subprocess.run(['systemctl', '--user', 'stop', name], capture_output=True)
        if not previous['enabled']:
            subprocess.run(['systemctl', '--user', 'disable', name], capture_output=True)
    for item in data['files']:
        target = home / item['path']
        if item['previous'] is None:
            target.unlink(missing_ok=True)
        else:
            target.write_bytes(base64.b64decode(item['previous']))
            target.chmod(item['mode'])
    command('systemctl', '--user', 'daemon-reload')
    for name, previous in data['services'].items():
        if previous['active']:
            command('systemctl', '--user', 'start', name)
    validate()
    manifest.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit('Run as your desktop user, without sudo.')
    home = Path.home()
    if args.uninstall:
        if args.dry_run:
            raise SystemExit('Use --dry-run for installation preview only.')
        restore(home, home / '.local/state/asus-vivobook-support/install.json')
    else:
        vendor = Path('/sys/class/dmi/id/sys_vendor').read_text().strip()
        model = Path('/sys/class/dmi/id/product_name').read_text().strip()
        if (vendor, model) != ('ASUSTeK COMPUTER INC.', 'ASUS Vivobook S 16 M5606UA_M5606UA'):
            raise SystemExit('This package is validated only for ASUS Vivobook S 16 M5606UA.')
        install(home, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
