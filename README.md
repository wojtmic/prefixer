# Prefixer
Prefixer is a tool for managing [Steam](https://store.steampowered.com/) [Proton](https://github.com/ValveSoftware/Proton) prefixes, alternative to [protontricks](https://github.com/Matoking/protontricks) with a friendlier interface, faster responses and modular approach.

## Why this?
Prefixer:
- includes **fuzzy name matching**, so you don't have to remember IDs
- is **up to 40 times faster** than legacy methods by modifying files directly (no wineserver)
- instead of "verbs" uses a declarative **json5 format** for tweaks, so you can share your work
- includes built-in first-class **Steam support**

## Usage
```bash
prefixer 'cyberpunk' tweak libs.d3dx9.47 # installs d3dcompiler 47 in Cyberpunk 2077
prefixer 'fallout new' run ~/Downloads/fonv_patcher.exe # runs the patcher for Fo:NV
prefixer 'subnautica' tweak loaders.bepinex # installs BepInEx 5 for Subnautica
prefixer 'Balatro' openpfx # opens the wineprefix folder in your file manager
```

Alongside more! Run `prefixer --help` or `prefixer --list-tweaks` for everything!

## Installation
The official way of downloading Prefixer is from the [AUR](https://aur.archlinux.org/packages/prefixer) under the package name `prefixer`. This approach only works on Arch Linux. If you use another distro, you are free to build the Python wheel yourself or wait for the pipx/PyPI release
