# Torrserver helper

Тулза для управления torrserver'ом с терминала
написан на питоне, спизжено и адаптировано [отсюда](https://github.com/iforvard/TorrServer-client/tree/main)

|           Команда | Функция                             |
| ----------------: | :---------------------------------- |
|     list_torrents | список всех торрентов: Name, (hash) |
| get_all_playlists | получить название и link для m3u    |
|      get_playlist | подробнее о плейлисте               |
|       get_torrent | подробнее о торренте                |
|      get_torrents | кратко: Name hash                   |
|    upload_torrent | для локальных .torrent файлов       |
|       add_torrent | для magnet-ссылок или http ссылок   |
|    remove_torrent | удалить торрент из списка           |
|      drop_torrent | дропнуть торрент                    |
