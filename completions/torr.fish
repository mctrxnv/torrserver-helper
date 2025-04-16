# === Основные подкоманды ===
complete -c torr -f -a "
  upload_torrent
  get_torrents
  list_torrents
  remove_torrent
  drop_torrent
  add_torrent
  get_torrent
  get_all_playlists
  get_playlist
"

# === upload_torrent — путь к файлу/папке ===
complete -c torr -n '__fish_seen_subcommand_from upload_torrent' -a '(__fish_complete_directories)'

# === add_torrent — только *.torrent файлы ===
function __torr_complete_torrents_only
    for f in (ls -1 | grep '\.torrent$' 2>/dev/null)
        echo $f
    end
end
complete -c torr -n '__fish_seen_subcommand_from add_torrent' -a '(__torr_complete_torrents_only)'

# === remove/drop/get_torrent/get_playlist — показывать title вместо hash ===
function __torr_title_to_hash
    for row in (torr -j get_torrents 2>/dev/null | jq -r '.[] | "\(.title)\t\(.hash)"')
        echo $row
    end
end

for cmd in remove_torrent drop_torrent get_torrent get_playlist
    complete -c torr -n "__fish_seen_subcommand_from $cmd" -a '(__torr_title_to_hash)'
end

# === upload_torrent — доп. аргументы ===
complete -c torr -n '__fish_seen_subcommand_from upload_torrent' -l title -d Заголовок
complete -c torr -n '__fish_seen_subcommand_from upload_torrent' -l poster -d 'Постер URL'
complete -c torr -n '__fish_seen_subcommand_from upload_torrent' -l no-save -d 'Не сохранять'

# === add_torrent — доп. аргументы ===
complete -c torr -n '__fish_seen_subcommand_from add_torrent' -l title -d Заголовок
complete -c torr -n '__fish_seen_subcommand_from add_torrent' -l poster -d 'Постер URL'
complete -c torr -n '__fish_seen_subcommand_from add_torrent' -l no-save -d 'Не сохранять'
