# KDE Plasma theming and layout recipes

## Discovery

```bash
printf 'desktop=%s\nsession=%s\n' "$XDG_CURRENT_DESKTOP" "$XDG_SESSION_TYPE"
plasmashell --version
kscreen-doctor -o
plasma-apply-lookandfeel --list
plasma-apply-colorscheme --list-schemes
gsettings get org.gnome.desktop.interface color-scheme
gsettings get org.gnome.desktop.interface gtk-theme
```

Inventory live panels without parsing the large applet configuration file:

```bash
QDBUS=$(command -v qdbus-qt6 || command -v qdbus)
"$QDBUS" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
'var out=[]; for (var p of panels()) { out.push(JSON.stringify({id:p.id,screen:p.screen,location:p.location,height:p.height,length:p.length,minLength:p.minimumLength,maxLength:p.maximumLength,alignment:p.alignment,hiding:p.hiding,opacity:p.opacityMode,floating:p.floating,widgets:p.widgets().map(w=>({id:w.id,type:w.type}))})); } print(out.join("\\n"));'
```

Read `launchers=` from the icon-task applet before replacing anything.

## Backups

Create a timestamped directory under `~/.local/state/` and copy only files that exist:

- `~/.config/kdeglobals`
- `~/.config/kwinrc`
- `~/.config/kcminputrc`
- `~/.config/plasma-org.kde.plasma.desktop-appletsrc`
- `~/.config/Kvantum/kvantum.kvconfig`

Keep the script used to transform panels beside the backup so the change is auditable.

## Theme layers

Typical KDE/GTK dark setup:

```bash
plasma-apply-colorscheme THEME_NAME
kvantummanager --set THEME_NAME
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle kvantum
kwriteconfig6 --file kdeglobals --group Icons --key Theme ICON_THEME
kwriteconfig6 --file kdeglobals --group General --key font 'FONT_FAMILY,11,-1,5,50,0,0,0,0,0'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
gsettings set org.gnome.desktop.interface gtk-theme 'GTK_THEME'
gsettings set org.gnome.desktop.interface icon-theme 'ICON_THEME'
gsettings set org.gnome.desktop.interface cursor-theme 'CURSOR_THEME'
gsettings set org.gnome.desktop.interface font-name 'FONT_FAMILY 11'
```

Use `plasma-apply-cursortheme CURSOR_THEME` when the theme is listed. If an installed hidden icon theme contains cursors but the selector omits it:

```bash
kwriteconfig6 --file kcminputrc --group Mouse --key cursorTheme CURSOR_THEME
```

## Plasma scripting pattern

Pass a reviewed JavaScript file to Plasma rather than embedding a long script directly in shell history:

```bash
script=$(<apply-layout.js)
"$QDBUS" org.kde.plasmashell /PlasmaShell \
  org.kde.PlasmaShell.evaluateScript "$script"
```

Useful panel properties in Plasma 6 include `screen`, `location`, `alignment`, `height`, `hiding`, `floating`, `opacityMode`, `minimumLength`, `maximumLength`, and `length`. Use `panel.widgets()`, `widget.remove()`, and `panel.addWidget(TYPE)` to reshape composition. Configure applets with `writeConfig(KEY, VALUE)`.

For a GNOME-like top bar, add widgets in this order:

1. `org.kde.plasma.kickoff`
2. `org.kde.plasma.panelspacer` with expanding enabled
3. `org.kde.plasma.digitalclock`
4. another expanding spacer
5. `org.kde.plasma.systemtray`

For the dock, retain or add `org.kde.plasma.icontasks`, center it, enable floating mode, and choose `dodgewindows` or `autohide`. Read the target screen geometry first and use that width for a full top bar.

## Verification

```bash
plasma-apply-colorscheme --list-schemes
kreadconfig6 --file kdeglobals --group KDE --key widgetStyle
kreadconfig6 --file kdeglobals --group Icons --key Theme
kreadconfig6 --file kdeglobals --group General --key font
kreadconfig6 --file kcminputrc --group Mouse --key cursorTheme
gsettings get org.gnome.desktop.interface gtk-theme
gsettings get org.gnome.desktop.interface icon-theme
gsettings get org.gnome.desktop.interface font-name
```

Run the panel inventory again and compare exact widget types and properties. Use `spectacle -b -n -o PATH.png` for a visual check without opening a screenshot UI, then inspect and remove the temporary image if it contains unrelated on-screen content.
