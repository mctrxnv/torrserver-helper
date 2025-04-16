{
  lib,
  stdenv,
  python3,
  bash,
}:

let
  pythonWithDeps = python3.withPackages (
    ps: with ps; [
      requests
    ]
  );
in

stdenv.mkDerivation rec {
  pname = "rutracker-torrent-downloader";
  version = "1.0";

  src = ./.;

  buildInputs = [
    pythonWithDeps
    bash
  ];

  installPhase = ''
    mkdir -p $out/bin $out/share/${pname}

    # Install all files to share directory
    cp api.py helper.py ruTrackDL.py cmd.sh $out/share/${pname}/

    # Create main executable that references files in share directory
    cat > $out/bin/torrMagnet <<EOF
    #!${bash}/bin/bash
    output=/tmp/torrTmp
    ${pythonWithDeps}/bin/python $out/share/${pname}/ruTrackDL.py "\$1" -o \$output
    ${pythonWithDeps}/bin/python $out/share/${pname}/helper.py add_torrent "\$(<\$output)"
    EOF

    chmod +x $out/bin/torrMagnet
  '';

  meta = with lib; {
    description = "RuTracker Torrent Downloader with TorrServer integration";
    homepage = "https://example.com";
    license = licenses.mit;
    maintainers = [ maintainers.yourname ];
    platforms = platforms.all;
  };
}
