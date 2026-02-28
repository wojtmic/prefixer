{
  description = "Prefixer - Steam Proton Prefix management tool";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = {
    self,
    nixpkgs,
  }: let
    inherit (nixpkgs) lib;

    systems = ["x86_64-linux" "aarch64-linux"];
    forAllSystems = f:
      lib.genAttrs systems (system:
        f {
          inherit system;
          pkgs = nixpkgs.legacyPackages.${system};
        });
  in {
    packages = forAllSystems ({
      system,
      pkgs,
    }: {
      default = self.packages.${system}.prefixer;
      prefixer = pkgs.python3Packages.callPackage ./nix {};
    });

    devShells = forAllSystems ({pkgs, ...}: {
      default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python3
          python3Packages.pip
          python3Packages.setuptools
          python3Packages.build
          python3Packages.pytest
          python3Packages.black
          python3Packages.ruff
          wine64
        ];
      };
    });

    apps = forAllSystems ({system, ...}: {
      default = {
        type = "app";
        program = lib.getExe self.packages.${system}.default;
      };
    });
  };
}
