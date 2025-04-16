#! /usr/bin/env bash
output=/tmp/torrTmp
python ruTrackDL.py "$1"        -o  $output
python helper.py    add_torrent "$(<$output)"
