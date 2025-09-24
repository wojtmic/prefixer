# Prefixer
Prefixer is a modern tool for managing [Steam](https://store.steampowered.com/) [Proton](https://github.com/ValveSoftware/Proton) prefixes, seeking to replace [protontricks](https://github.com/Matoking/protontricks) with a friendlier interface, faster responses and modular approach.

# Usage
Prefixer was designed to be as user-friendly as possible, so it should be easy to get started.<br>
Here are some examples:
```bash
prefixer "Cyberpunk 2077" tweak d3dcompiler # Installs the DirectX Compiler in Cyberpunk
prefixer 361420 openpfx # Opens the prefix directory for Astroneer (361420) in your default file manager
prefixer "Subnautica" tweak bepinex # Installs BepInEx 5 for Subnautica
prefixer "Undertale" run ~/Downloads/mod-installer.exe # Runs a .exe file with the context of Undertale's wineprefix
```
<br>
Full built-in tweak list:<br>
- `bepinex`: Installs BepInEx 5.4.23.3
- `d3dcompiler`: Installs the Microsoft DirectX End-User Runtime
- `dotnet48`: Installs the Microsoft .NET Framework 4.8
- `vcrun2022`: Installs the Microsoft Visual C++ 2022 Redistributable
- `winhttp`: Adds a `winhttp` library override to the prefix.

# Installation
The official way of downloading Prefixer is from the AUR under the package name `prefixer`. This approach only works on Arch Linux. If you use another distro, you are free to build the Python wheel yourself, but Arch is the primary distribution for Prefixer and is prioritized.
