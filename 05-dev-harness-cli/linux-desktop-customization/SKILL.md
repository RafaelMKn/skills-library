---
name: linux-desktop-customization
description: "Use when customizing Linux desktop themes and panels."
version: 1.0.0
metadata:
  hermes:
    tags: [linux, desktop, kde, plasma, gnome, themes]
    category: linux
---

# Linux desktop customization

## Workflow

1. **Identify the live desktop before interpreting the requested style.** Read `XDG_CURRENT_DESKTOP`, `XDG_SESSION_TYPE`, the shell version, current GTK settings, KDE settings when present, enabled extensions, outputs, and panel/widget state. If the user asks for “GNOME” while running KDE, distinguish installing GNOME from making KDE look GNOME-like before changing anything.

2. **Clarify only decisions that materially change the implementation.** Establish light/dark, visual fidelity versus preserving the current palette, panel-only versus full toolkit styling, and whether panels should appear on the primary display or every display.

3. **Back up the exact live configuration before panel or shell edits.** For Plasma, preserve `~/.config/kdeglobals`, `~/.config/kwinrc`, `~/.config/kcminputrc`, `~/.config/plasma-org.kde.plasma.desktop-appletsrc`, and the Kvantum config when present. Store the rollback path in the completion report.

4. **Apply appearance as separate layers instead of treating “theme” as one switch.** Configure:
   - Qt/KDE widget style and color scheme;
   - GTK/libadwaita dark preference and GTK theme;
   - icons, cursor, and fonts;
   - window decoration behavior;
   - shell panels, dock behavior, widgets, and wallpaper only when requested.

   Keep compatibility in view: a GNOME icon set can omit KDE-specific actions, so prefer a compatible GNOME-like set unless the user explicitly prioritizes fidelity.

5. **Change Plasma panels through the live Plasma scripting API.** First inventory panel IDs, screens, widget types, hiding mode, alignment, length, and pinned launchers. Preserve launchers before removing or rebuilding widgets. Reuse an existing task-manager panel as the dock when that avoids losing its configuration; create the top bar separately.

6. **Model GNOME-like Plasma layouts deliberately.** A practical primary-screen layout is:
   - top bar: application launcher, expanding spacer, clock, expanding spacer, system tray;
   - bottom dock: icon-only task manager, centered, floating, and `dodgewindows` or `autohide` according to preference.

   Never hard-code a panel width without reading the target output geometry. On multi-monitor systems, set the panel screen explicitly; GNOME-like primary-only behavior is a valid default, but state it.

7. **Reload only what is necessary.** Ask KWin to reconfigure after decoration/style changes. Do not restart the whole desktop session merely to make already-open applications repaint; report that existing Qt/GTK applications may need to be reopened and that cursor changes can require a new session.

8. **Verify configuration and live state independently.** Read settings back with `kreadconfig6`, `gsettings get`, Kvantum config, and Plasma’s panel API. Then capture the desktop with the native screenshot utility and inspect panel placement. A configured auto-hidden dock not appearing in a screenshot is not a failure if the live panel API confirms its state and the hiding condition explains it.

9. **Report only the changed layers, verification result, restart caveats, and rollback path.** Do not narrate command-by-command work.

## Pitfalls

- Detect the installed Qt DBus CLI name before scripting Plasma — distributions expose names such as `qdbus-qt6`, and guessing the executable wastes a round trip.
- If Plasma’s cursor chooser rejects an installed cursor because the icon theme is hidden from selectors, write `cursorTheme` to `kcminputrc` and verify with `kreadconfig6`; selector visibility and cursor availability are separate mechanisms.
- Use `kreadconfig6` for reads and `kwriteconfig6` for writes — invoking the writer without a value prints usage instead of verifying state.
- Do not delete a panel before extracting icon-task launchers — launcher order lives in applet configuration and is easy to lose during reconstruction.
- Verify panel composition programmatically after a DBus script — a successful script return proves evaluation, not that every requested property persisted.

For Plasma-specific commands and scripting patterns, read [references/kde-plasma-layouts.md](references/kde-plasma-layouts.md).
