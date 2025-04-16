# Torrserver helper

> еще не стабильно канешна, но юзабельно

Тулза для управления torrserver'ом с терминала
написан на питоне, спизжено и адаптировано [отсюда](https://github.com/iforvard/TorrServer-client/tree/main)

|             Команда | Функция                             |
| ------------------: | :---------------------------------- |
|     _list_torrents_ | список всех торрентов: Name, (hash) |
| _get_all_playlists_ | получить название и link для m3u    |
|      _get_playlist_ | подробнее о плейлисте               |
|       _get_torrent_ | подробнее о торренте                |
|      _get_torrents_ | кратко: Name hash                   |
|    _upload_torrent_ | для локальных .torrent файлов       |
|       _add_torrent_ | для magnet-ссылок или http ссылок   |
|    _remove_torrent_ | удалить торрент из списка           |
|      _drop_torrent_ | дропнуть торрент                    |
