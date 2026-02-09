{
  description = "Prefixer - Steam Proton Prefix management tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "prefixer";
          version = "1.3.4";
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = with pkgs.python3Packages; [
            setuptools
            wheel
          ];

          propagatedBuildInputs = with pkgs.python3Packages; [
            click
            rich
            requests
            pyyaml
          ];

          makeWrapperArgs = [
            "--prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.wine64 pkgs.winetricks ]}"
          ];

          doCheck = false;

          pythonImportsCheck = [ "prefixer" ];

          meta = with pkgs.lib; {
            description = "Steam Proton Prefix management tool with fuzzy name matching";
            homepage = "https://github.com/wojtmic/prefixer";
            changelog = "https://github.com/wojtmic/prefixer/blob/master/CHANGELOG.md";
            license = licenses.gpl3Only;
            platforms = platforms.linux;
            mainProgram = "prefixer";
            maintainers = [ ];
          };
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.pip
            python3Packages.setuptools
            python3Packages.build
            python3Packages.pytest
            python3Packages.black
            python3Packages.ruff
            wine64
            winetricks
          ];
        };

        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/prefixer";
        };
      }
    );
}
