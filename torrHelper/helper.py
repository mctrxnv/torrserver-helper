#!/usr/bin/env python3

import json
import argparse
from api import Client
from urllib.parse import unquote, parse_qs, urlparse
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, quote
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, unquote

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

def get_safe_title(link: str) -> str:
  try:
    parsed = urlparse(link)
    qs = parse_qs(parsed.query)
    dn = qs.get("dn", ["Magnet"])[0]
    return unquote(dn)[:120]
  except Exception:
    return "Magnet"

def truncate_utf8(s: str, max_bytes: int) -> str:
  encoded = s.encode("utf-8")
  if len(encoded) <= max_bytes:
    return s
  truncated = encoded[:max_bytes]
  # remove partial character
  while truncated and (truncated[-1] & 0b11000000) == 0b10000000:
    truncated = truncated[:-1]
  return truncated.decode("utf-8", errors="ignore")

def sanitize_magnet(link: str) -> str:
  parsed = urlparse(link)
  if parsed.scheme != "magnet":
    return link
  query = parse_qsl(parsed.query)
  cleaned = []
  for k, v in query:
    if k == "dn":
      # пропустить слишком длинные display name
      if len(unquote(v).encode("utf-8")) > 400:
        continue
    cleaned.append((k, v))
  return urlunparse((parsed.scheme, '', parsed.path, '', urlencode(cleaned, doseq=True), ''))

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

  fr = subparsers.add_parser("fetch_rutracker")
  fr.add_argument("topic", help="ID или URL темы на rutracker.org")
  fr.add_argument("--title", help="Название для загрузки")
  fr.add_argument("--poster", help="Постер (необязательно)")

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
      import os
      from pathlib import Path
      if args.link.endswith(".torrent") and Path(args.link).is_file():
        # перенаправим на upload_torrent
        result = client.upload_torrent(
          path=args.link,
          title=args.title,
          poster=args.poster,
          save_to_db=not args.no_save
        )
      else:
        title = args.title or truncate_utf8(get_safe_title(args.link), 240)
        poster = args.poster or ""
        save = not args.no_save
        result = client.add_torrent(
          link = sanitize_magnet(args.link),
          title=title,
          poster=poster,
          save_to_db=save
        )
        print_result(result, json_out)

    case "get_torrent":
      result = client.get_torrent(args.hash)
      print_result(result, json_out)

    case "fetch_rutracker":
      import os, re
      import requests
      import tempfile
      from html.parser import HTMLParser

      username = os.getenv("RUTRACKER_USERNAME")
      password = os.getenv("RUTRACKER_PASSWORD")

      if not username or not password:
        print("❌ Не заданы переменные окружения RUTRACKER_USERNAME и/или RUTRACKER_PASSWORD")
        return

      topic_arg = args.topic
      if topic_arg.startswith("http"):
        m = re.search(r"[?&]t=(\d+)", topic_arg)
        topic_id = m.group(1) if m else None
      else:
        topic_id = topic_arg if topic_arg.isdigit() else None

      if not topic_id:
        print("❌ Неверный ID темы RuTracker")
        return

      session = requests.Session()
      login_url = "https://rutracker.org/forum/login.php"
      payload = {
        "login_username": username,
        "login_password": password,
        "login": "Вход"
      }
      headers = {
        "Referer": "https://rutracker.org/forum/index.php"
      }

      print("🔐 Авторизация на rutracker.org...")
      r = session.post(login_url, data=payload, headers=headers)
      if "bb_data" not in session.cookies:
        print("❌ Авторизация не удалась.")
        return

      print("🌐 Получение страницы темы...")
      topic_url = f"https://rutracker.org/forum/viewtopic.php?t={topic_id}"
      r = session.get(topic_url)
      if not r.ok:
        print(f"❌ Не удалось загрузить тему {topic_id}")
        return

      class TorrentLinkParser(HTMLParser):
        def __init__(self):
          super().__init__()
          self.links = []

        def handle_starttag(self, tag, attrs):
          if tag == "a":
            for k, v in attrs:
              if k == "href" and v.startswith("dl.php?t="):
                self.links.append(v)

      parser = TorrentLinkParser()
      parser.feed(r.text)

      if not parser.links:
        print("❌ Не найдена ссылка на .torrent")
        return

      dl_link = parser.links[0]
      torrent_url = "https://rutracker.org/forum/{dl_link}"

      print(f"📥 Скачивание .torrent с {torrent_url}")
      r = session.get(torrent_url)
      if not r.ok:
        print("❌ Не удалось скачать .torrent")
        return

      with tempfile.NamedTemporaryFile(suffix=".torrent", delete=False) as tmp:
        tmp.write(r.content)
        tmp.flush()
        result = client.upload_torrent(
          path=tmp.name,
          title=args.title or f"RuTracker:{topic_id}",
          poster=args.poster or "",
          save_to_db=True
        )
        print_result(result, json_out)

if __name__ == "__main__":
  main()

