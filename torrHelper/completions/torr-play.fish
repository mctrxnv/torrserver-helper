function __torr_list_hashes
    torr get_torrents 2>/dev/null | jq -r '.[].hash'
end

complete -c torr-play -f -a '(__torr_list_hashes)'
