## [1.3.4] - 2026-02-08

### 🚀 Features

- *(cli)* Add list-tweaks flag
- *(core)* Raise exception on no tweak found
- *(tasks)* Add user agent to download
- *(tasks)* Update user agent
- Support non-Steam shortcuts
- *(tweaks)* Add fonts.arial tweak
- *(tweaks)* Add corefonts
- *(tweaks)* Add physx
- *(cli)* Allow running multiple tweaks

### 🐛 Bug Fixes

- *(tasks)* Install_font registry edit call
- *(tasks)* Install_font regedit
- *(cli)* Bump version correctly
- *(tasks)* Allow redirects in download logic
- *(pipx)* Package tweaks data correctly
- *(pipx)* Bump ver for pipx pypi
- *(pipx)* Bump ver for pipx pypi (2)
- *(pipx)* Bump ver for pipx pypi (3)
- *(tweaks)* Decrease packaged tweaks priority to lowest

### 📚 Documentation

- *(readme)* Rewrite for clarity & add highlights
- *(readme)* Update pipx info

### ⚡ Performance

- Dont read tweak files when autocompleting
- Skip reading unnecessary tweaks

### 🎨 Styling

- *(cli)* Print on user abort
- *(tasks)* Add -q for cabextract for ux
- *(cli)* Remove extra space

### ⚙️ Miscellaneous Tasks

- Bump ver
- Remove accidental pushed file
- Add uv.lock to git
- Add info for pypi
- Bump ver
- Add cliff.toml
