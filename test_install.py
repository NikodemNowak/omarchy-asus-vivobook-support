import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import install


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        main = self.home / '.config/hypr/hyprland.lua'
        main.parent.mkdir(parents=True)
        main.write_text('-- existing settings\n')
        self.menu = self.home / '.config/omarchy/extensions/omarchy-menu.jsonc'
        self.menu.parent.mkdir(parents=True)
        self.menu.write_text('// user menu\n{"personal":{"label":"Keep me"},}\n')
        self.original = {str(p.relative_to(self.home)): p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        self.addCleanup(patch.stopall)
        patch('install.command', return_value='').start()
        patch('install.subprocess.run', return_value=subprocess.CompletedProcess([], 1)).start()

    def test_install_then_uninstall_preserves_original_files(self):
        install.install(self.home)
        self.assertEqual(json.loads(self.menu.read_text())['personal']['label'], 'Keep me')
        install.restore(self.home, self.home / '.local/state/asus-vivobook-support/install.json')
        for relative, value in self.original.items():
            self.assertEqual((self.home / relative).read_bytes(), value)
        self.assertFalse((self.home / '.config/hypr/vivobook.lua').exists())

    def test_uninstall_refuses_to_overwrite_later_edits(self):
        install.install(self.home)
        self.menu.write_text('{"personal":{"label":"Changed later"}}')
        with self.assertRaises(SystemExit):
            install.restore(self.home, self.home / '.local/state/asus-vivobook-support/install.json')
        self.assertIn('Changed later', self.menu.read_text())

    def test_invalid_menu_fails_before_any_changes(self):
        self.menu.write_text('invalid json')
        with self.assertRaises(json.JSONDecodeError):
            install.install(self.home)
        self.assertEqual((self.home / '.config/hypr/hyprland.lua').read_text(), '-- existing settings\n')
        self.assertFalse((self.home / '.local/state/asus-vivobook-support/install.json').exists())


if __name__ == '__main__':
    unittest.main()
