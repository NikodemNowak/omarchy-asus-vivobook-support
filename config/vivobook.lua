-- Local ASUS support; packaged Omarchy files stay managed by updates.
local support_bin = os.getenv("HOME") .. "/.local/share/asus-vivobook-support/bin"
local omarchy_bin = (os.getenv("OMARCHY_PATH") or "/usr/share/omarchy") .. "/bin"
local entries = { support_bin, omarchy_bin }
for entry in (os.getenv("PATH") or "/usr/local/bin:/usr/bin"):gmatch("[^:]+") do
  if entry ~= support_bin and entry ~= omarchy_bin then
    table.insert(entries, entry)
  end
end
hl.env("PATH", table.concat(entries, ":"))

-- Linux names for ASUS display and MyASUS hotkeys.
o.bind("XF86Display", "Displays", "omarchy-menu toggle vivobook.displays")
o.bind("XF86DisplayToggle", "Displays", "omarchy-menu toggle vivobook.displays")
-- ASUS projection keys can emit Windows+P; Omarchy normally uses this for pseudo windows.
hl.unbind("SUPER + P")
o.bind("SUPER + P", "Displays", "omarchy-menu toggle vivobook.displays")
o.bind("XF86Launch1", "Laptop hardware", "omarchy-menu toggle vivobook")

-- F8: hwdb remaps KEY_BLUETOOTH to KEY_PROG2 (XF86Launch2). F10: KEY_F14 (184 + XKB offset 8 = code:192).
-- The default XKB map names KEY_F14 XF86Launch5, so bind its code directly.
o.bind("XF86Launch2", "Emojis", "omarchy-shell shell toggle omarchy.emojis")
o.bind("code:192", "Microphone modes", "omarchy-menu toggle vivobook.microphone")

-- ASUS emoji keys can also emit the Windows emoji shortcut.
o.bind("SUPER + PERIOD", "Emojis", "omarchy-shell shell toggle omarchy.emojis")
