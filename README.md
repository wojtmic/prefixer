 <picture>
    <source media="(prefers-color-scheme: dark)" srcset="branding/banner.svg">
    <source media="(prefers-color-scheme: light)" srcset="branding/banner-light.svg">
    <img alt="Project Banner" src="branding/banner-light.svg" width="400">
  </picture>

![PyPI](https://img.shields.io/pypi/v/prefixer)
![Python Version](https://img.shields.io/pypi/pyversions/prefixer)
![License](https://img.shields.io/github/license/wojtmic/prefixer)
![Tests](https://img.shields.io/github/actions/workflow/status/wojtmic/prefixer/tests.yml)

Prefixer is a tool for managing [Steam](https://store.steampowered.com/) [Proton](https://github.com/ValveSoftware/Proton) prefixes, alternative to [protontricks](https://github.com/Matoking/protontricks) with a friendlier interface, faster responses and modular approach.

## Why this?
Prefixer:
- includes **fuzzy name matching**, so you don't have to remember IDs
- is **up to 40 times faster** than legacy methods by modifying files directly (no wineserver)
- instead of "verbs" uses a declarative **json5 format** for tweaks, so you can share your work
- includes built-in first-class **Steam support**
![output](https://github.com/user-attachments/assets/69e49b07-e332-4bc2-80d5-b9e1f16b0578)
*Overriding winhttp for BepInEx, compared to protontricks*

## Usage
```bash
prefixer 'cyberpunk' tweak libs.d3dx9.47 # installs d3dcompiler 47 in Cyberpunk 2077
prefixer 'fallout new' run ~/Downloads/fonv_patcher.exe # runs the patcher for Fo:NV
prefixer 'subnautica' tweak loaders.bepinex # installs BepInEx 5 for Subnautica
prefixer 'Balatro' openpfx # opens the wineprefix folder in your file manager
```

Alongside more! Run `prefixer --help` or `prefixer --list-tweaks` for everything!

## Installation
### Arch 
install `prefixer` with your favorite AUR helper, for example:
```bash
yay -S prefixer
```
### NixOS 
add an input (pinned to the most recent release for stability):
```nix
inputs.prefixer.url = "github:wojtmic/prefixer/1.3.6";
```

Then add the package:
```nix
home.packages = [
  inputs.prefixer.packages.${pkgs.system}.default
];
```

### Any other distro
Use `pipx` (or `uv`) to get it from PyPI:
```bash
pipx install prefixer
```

## Community
Prefixer is a fairly new project, you can become an early adopter now!

### Star graph
[![Star History Chart](https://api.star-history.com/svg?repos=wojtmic/prefixer&type=Date)](https://star-history.com/#wojtmic/prefixer&Date)

### Contributors
- [Wojtmic](https://github.com/wojtmic) - Maintainer, founder, all Python
- [Tymon3310](https://github.com/tymon3310) - Multiple tweaks
- [Keygenesis (david)](https://github.com/keygenesis) - NixOS Flake
