{
  lib,
  buildPythonApplication,
  setuptools,
  wheel,
  vdf,
  json5,
  requests,
  click,
  rapidfuzz,
  wine64,
  steam-run-free,
}: let
  pyproject = (lib.importTOML ../pyproject.toml).project;
in
  buildPythonApplication (finalAttrs: {
    pname = "prefixer";
    inherit (pyproject) version;
    pyproject = true;

    src = lib.cleanSource ../.;

    patches = [./steam-run.patch];

    nativeBuildInputs = [
      setuptools
      wheel
    ];

    propagatedBuildInputs = [
      vdf
      json5
      requests
      click
      rapidfuzz
    ];

    makeWrapperArgs = [
      "--prefix PATH : ${lib.makeBinPath [wine64 steam-run-free]}"
    ];

    doCheck = false;
    dontCheckRuntimeDeps = true;

    pythonImportsCheck = ["prefixer"];

    meta = {
      description = "Steam Proton Prefix management tool with fuzzy name matching";
      homepage = "https://github.com/wojtmic/prefixer";
      changelog = "https://github.com/wojtmic/prefixer/blob/${finalAttrs.version}/CHANGELOG.md";
      license = lib.licenses.gpl3Only;
      platforms = lib.platforms.linux;
      mainProgram = "prefixer";
    };
  })
