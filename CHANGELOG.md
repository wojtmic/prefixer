## [1.3.7] - 2026-02-10

### 🐛 Bug Fixes

- *(cli)* Add help text to -q
- *(tweaks)* Fix bepinex malformed
- Improperly override tweaks

### 📚 Documentation

- Add branding svgs
- *(readme)* Add community section
- *(readme)* Add badges
- *(readme)* Change graph to dark

### 🎮 Tweaks

- Add many tweaks (#6)

## [1.3.6] - 2026-02-09

### 🚀 Features

- *(cli)* Add help text
- Add NixOS support (Merge pull request #5 from keygenesis/master)
- *(cli)* Add overridedll command

### 🐛 Bug Fixes

- Properly set non-Steam pfx path
- *(coldpfx)* Prefixer_remove not working
- *(cli)* Overridedll command

### 📚 Documentation

- *(readme)* Improve install instructions

### ⚙️ Development Process

- Add pypi release workflow
- Update pr-title workflow to allow tweak
## [1.3.5] - 2026-02-09

### 🚀 Features

- *(cli)* Add proper exit codes
- *(cli)* Add --search arg
- *(cli)* Add --validate-tweak

### 🐛 Bug Fixes

- *(cli)* Crash when --search not specified
- *(cli)* Validate tweak types properly

### 📚 Documentation

- *(readme)* Improve installation instructions
- *(readme)* Correct pypi install instructions
- Add contributing guide
- *(readme)* Add comparison showcase gif
- *(contributing)* Add info on tweak commit type

### 🎨 Styling

- Change winhttp description

### 🧪 Testing

- Move regedit to top level
- Add basic performance check
- Add test workflow
- Add validate-tweaks workflow

### ⚙️ Development Process

- Add tweak commit type for patch notes
- Add automated release generation action
- Skip showing release fixes
- Change chore header
- Don't show bump ver chores
- Add autogeneration of title from git cliff header on release
- Add pr title validator
- Add pr template
- Add security group to changelog
- Add issue templates

### 🛡️ Security

- *(tasks)* Removed shell task
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
- *(changelog)* Add changelog

### ⚡ Performance

- Dont read tweak files when autocompleting
- Skip reading unnecessary tweaks

### 🎨 Styling

- *(cli)* Print on user abort
- *(tasks)* Add -q for cabextract for ux
- *(cli)* Remove extra space

### ⚙️ Development Process

- Remove accidental pushed file
- Add uv.lock to git
- Add info for pypi
- Add cliff.toml
## [1.0.0] - 2025-09-14
