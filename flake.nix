{
  description = ''
    TorrServer Helper CLI
    (adapted from here https://github.com/iforvard/TorrServer-client)
  '';

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    inputs:
    inputs.flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import inputs.nixpkgs {
          inherit
            system
            ;
        };

        pypkgs = pkgs.python312Packages;

        rutracker-downloader = pkgs.python312Packages.buildPythonPackage {
          pname = "rutracker-downloader";
          version = "3.0.4";
          src = pkgs.fetchPypi {
            pname = "rutracker-downloader";
            version = "3.0.4";
            sha256 = "sha256-52Etli3SO6w28y29jTkF8W3oFaKChUUhMBu+aK2IuJc=";
          };

          doCheck = false;
          propagatedBuildInputs = with pkgs.python312Packages; [
            requests
            beautifulsoup4
          ];
        };
      in
      {
        packages.default = pypkgs.buildPythonApplication {
          pname = "torrserver-helper";
          version = "1.0.0";
          format = "other"; # нет pyproject.toml

          src = ./.;

          propagatedBuildInputs = [ pypkgs.requests ];

          installPhase = ''
            mkdir   -p     $out/bin
            cp             api.py                        $out/bin

            # Уствнока скриптов
            install -m755  helper.py                     $out/bin/torr
            install -Dm755 bin/torr-shell                $out/bin/torr-shell
            install -Dm755 bin/torr-play                 $out/bin/torr-play

            # Установка автодополнений
            install -Dm644 completions/torr.fish         $out/share/fish/vendor_completions.d/torr.fish
            install -Dm644 completions/torr-shell.fish   $out/share/fish/vendor_completions.d/torr-shell.fish
            install -Dm644 completions/torr-play.fish    $out/share/fish/vendor_completions.d/torr-play.fish
          '';

          meta.mainProgram = "torr";
        };
      }
    );
}
