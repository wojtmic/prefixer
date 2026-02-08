# Prefixer Contribution Guide
We appreciate all contributions, whenever you're optimizing, adding features, fixing bugs or simply making more tweaks! However, for the sake of organization, there are a few guidelines you must follow when making a PR.

## The guidelines
- If you are contributing tweaks, make sure to follow their [specific guidelines](https://github.com/wojtmic/prefixer/wiki/Tweak-Contribution-Guildelines)
- Use [Conventional Commits](https://conventionalcommits.org/) for the sake of automated patch notes
- Under any circumstance, **do not shell out to winetricks** - we are building a modern alternative
- If possible, it's best to reimplement something in Python or use a dependency (reimplementing > dependency > subprocess)
- Functions must have type-hinted arguments, return type is not required
- Use dataclasses instead of dicts (unless parsing data from files)
- Modularize the code; don't create monoliths

## CLI-specifics
- User is king, take UX seriously
- When the `-q` flag is specified, assume you are dealing with a script - echo the bare minimum
- Don't use emojis, it's fine to use Nerdfonts
### Colors?
The use of color is encouraged, but don't spam it.
- `bright_blue` or bolding for highlights 
- `bright_black` for technical information
- `bright_red` for serious warnings and errors
- `bright_green` for important successes

## AI?
AI-assisted development IS allowed, however **YOU/The person submitting the PR** is responsible for everything and is expected to understand the code.