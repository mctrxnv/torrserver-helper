#!/usr/bin/env python3

import json
import argparse
from api import Client


def print_result(data, as_json: bool):
  if as_json:
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return

  if isinstance(data, list) and all(isinstance(d, dict) for d in data):
    # Проверим, есть ли поля hash и title
    show_hash = any("hash" in d for d in data)
    show_title = any("title" in d for d in data)

    if show_hash and show_title:
      # Вычислим ширину столбца title
      max_title = max(len(d.get("title", "")) for d in data)
      for d in data:
        title = d.get("title", "")
        hash_ = d.get("hash", "")
        print(f"{title.ljust(max_title)}  {hash_}")
      return

  # Фоллбэк
  if isinstance(data, list):
    for item in data:
      print(str(item))
  elif isinstance(data, dict):
    max_key = max(len(str(k)) for k in data)
    for k, v in data.items():
      val = json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else str(v)
      print(f"{str(k).ljust(max_key)} : {val}")
  else:
    print(str(data))

def main():
  parser = argparse.ArgumentParser(description="TorrServer CLI Helper")
  parser.add_argument("--host", default="http://127.0.0.1:8090", help="Адрес TorrServer")
  parser.add_argument("-j", "--json", action="store_true", help="Вывод в формате JSON")

  subparsers = parser.add_subparsers(dest="command", required=True)

  # Команды
  subparsers.add_parser("get_all_playlists")

  gp = subparsers.add_parser("get_playlist")
  gp.add_argument("hash", help="Torrent hash")
  gp.add_argument("--from-last", action="store_true", help="Исключить просмотренные")

  ut = subparsers.add_parser("upload_torrent")
  ut.add_argument("path", help="Путь к .torrent файлу")
  ut.add_argument("--title", default="", help="Название торрента")
  ut.add_argument("--poster", default="", help="Постер URL")
  ut.add_argument("--no-save", action="store_true", help="Не сохранять в базу")

  subparsers.add_parser("get_torrents")
  subparsers.add_parser("list_torrents")

  rt = subparsers.add_parser("remove_torrent")
  rt.add_argument("hash", help="Torrent hash")

  dt = subparsers.add_parser("drop_torrent")
  dt.add_argument("hash", help="Torrent hash")

  at = subparsers.add_parser("add_torrent")
  at.add_argument("link", help="Magnet или ссылка")
  at.add_argument("--title", default="", help="Название")
  at.add_argument("--poster", default="", help="Постер")
  at.add_argument("--no-save", action="store_true", help="Не сохранять в базу")

  gt = subparsers.add_parser("get_torrent")
  gt.add_argument("hash", help="Torrent hash")

  args = parser.parse_args()
  json_out = args.json
  client = Client(args.host)

  match args.command:
    case "get_all_playlists":
      print(client.get_all_playlists())

    case "get_playlist":
      result = client.get_playlist(args.hash, from_last=args.from_last)
      print(result)

    case "upload_torrent":
      result = client.upload_torrent(
        path=args.path,
        title=args.title,
        poster=args.poster,
        save_to_db=not args.no_save
      )
      print_result(result, json_out)

    case "get_torrents":
      result = client.get_torrents()
      print_result(result, json_out)

    case "list_torrents":
      result = client.list_torrents()
      if json_out:
        print(json.dumps([t.__dict__ for t in result], ensure_ascii=False, indent=2))
      else:
        for t in result:
          print(f"{t.title} ({t.hash}) — {len(t.files)} files, {t.torrent_size} bytes")

    case "remove_torrent":
      print(client.remove_torrent(args.hash))

    case "drop_torrent":
      print(client.drop_torrent(args.hash))

    case "add_torrent":
      result = client.add_torrent(
        link=args.link,
        title=args.title,
        poster=args.poster,
        save_to_db=not args.no_save
      )
      print_result(result, json_out)

    case "get_torrent":
      result = client.get_torrent(args.hash)
      print_result(result, json_out)


if __name__ == "__main__":
  main()

