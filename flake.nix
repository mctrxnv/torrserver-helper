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
      in
      {
        packages = {
          default = pypkgs.buildPythonApplication {
            pname = "torrserver-helper";
            version = "1.0.0";
            format = "other"; # нет pyproject.toml

            src = ./torrHelper;

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
          torrMagnet =
            let
              pyEnv = pkgs.python3.withPackages (
                ps: with ps; [
                  requests
                ]
              );
            in
            pkgs.stdenv.mkDerivation rec {
              pname = "torrMagnet";
              version = "1.0";

              src = ./torrMagnet;

              buildInputs = [
                pkgs.bash
                pyEnv
              ];

              installPhase = ''
                mkdir -p $out/bin $out/share/${pname}

                # Install all files to share directory
                cp api.py helper.py ruTrackDL.py $out/share/${pname}/

                # Create main executable that references files in share directory
                cat > $out/bin/torrMagnet <<EOF
                #!${pkgs.runtimeShell}
                output=/tmp/torrTmp
                ${pyEnv}/bin/python $out/share/${pname}/ruTrackDL.py "\$1" -o \$output
                ${pyEnv}/bin/python $out/share/${pname}/helper.py add_torrent "\$(<\$output)"
                EOF

                chmod +x $out/bin/torrMagnet
              '';
            };
        };
      }
    );
}
