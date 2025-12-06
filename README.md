# Prefixer
Prefixer is a tool for managing [Steam](https://store.steampowered.com/) [Proton](https://github.com/ValveSoftware/Proton) prefixes, seeking to replace [protontricks](https://github.com/Matoking/protontricks) with a friendlier interface, faster responses and modular approach. (not there yet, but working on it!)

# Usage
Prefixer was designed to be as user-friendly as possible, so it should be easy to get started.<br>
Here are some examples:
```bash
prefixer "Cyberpunk 2077" tweak libs.d3dx9.47 # Installs the DirectX Compiler in Cyberpunk
prefixer 361420 openpfx # Opens the prefix directory for Astroneer (361420) in your default file manager
prefixer "Subnautica" tweak loaders.bepinex # Installs BepInEx 5 for Subnautica
prefixer "Undertale" run ~/Downloads/mod-installer.exe # Runs a .exe file with the context of Undertale's wineprefix
```
<br>
Full built-in tweak list:

```
tweaks
├── games
│   ├── cyberpunk2077.json5
│   └── fallout4.json5
├── libs
│   ├── d3dx9
│   │   ├── 43.json5
│   │   └── 47.json5
│   ├── dotnet
│   │   ├── 40.json5
│   │   ├── 48.json5
│   │   ├── 60.json5
│   │   └── 80.json5
│   └── ms
│       ├── vcrun2008.json5
│       ├── vcrun2010.json5
│       ├── vcrun2012.json5
│       ├── vcrun2013.json5
│       ├── vcrun2022.json5
│       └── vcrun_all.json5
├── loaders
│   └── bepinex.json5
├── misc
│   └── winhttp.json5
├── reghacks
│   ├── backend_vulkan.json5
│   ├── fake_2gb_vram.json5
│   ├── mouse_warp.json5
│   ├── win10.json5
│   ├── win11.json5
│   └── win7.json5
└── themes
    ├── breeze_dark.json5
    ├── fonts.json5
    └── reset.json5
```

Tweaks are auto-completed in Bash, Zsh and Fish.

# Installation
The official way of downloading Prefixer is from the [AUR](https://aur.archlinux.org/packages/prefixer) under the package name `prefixer`. This approach only works on Arch Linux. If you use another distro, you are free to build the Python wheel yourself, but Arch is the primary distribution for Prefixer and is prioritized.
