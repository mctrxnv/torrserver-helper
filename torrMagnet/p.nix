{ pkgs }:

let
  pypkgs = pkgs.python312Packages;
  pyEnv = pkgs.python3.withPackages (ps: with ps; [ requests ]);
  cmd = pkgs.writeShellScriptBin "cmd" ''
    #!${pkgs.runtimeShell}
    output=/tmp/torrTmp
    ${pyEnv}/bin/python ruTrackDL.py "$1"        -o  $output
    ${pyEnv}/bin/python helper.py    add_torrent "$(<$output)"
  '';
in

pypkgs.buildPythonApplication {
  pname = "torrMagnet";
  version = "1.0.0";
  format = "other"; # нет pyproject.toml

  src = ./.;
  buildInputs = with pkgs; [
    pyenv
    bash
  ];

  installPhase = ''
    mkdir -p $out/bin
    cp ruTrackDL.py helper.py api.py $out/bin
    install -Dm755 ${cmd}/bin/cmd $out/bin/torrMagnet
  '';
}
