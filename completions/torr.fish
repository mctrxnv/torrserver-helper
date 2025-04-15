complete -c torr -f -a "upload_torrent get_torrents list_torrents remove_torrent drop_torrent add_torrent get_torrent get_all_playlists get_playlist"
complete -c torr -n '__fish_seen_subcommand_from upload_torrent' -a '(__fish_complete_directories)'

function __torr_list_hashes
    torr get_torrents 2>/dev/null | jq -r '.[].hash'
end

complete -c torr -n '__fish_seen_subcommand_from remove_torrent drop_torrent get_torrent get_playlist' -a '(__torr_list_hashes)'
