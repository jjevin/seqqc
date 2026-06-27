{
  description = "Seqqc development environment";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in
  {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        python311
        zlib
        gcc
      ];

      env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
        pkgs.stdenv.cc.cc.lib
        pkgs.libz
      ];

      shellHook = ''
        if [ ! -d .venv ]; then
          python -m venv .venv
          pip install -e ".[dev]"
        fi
        source .venv/bin/activate
      '';
    };
  };
}
