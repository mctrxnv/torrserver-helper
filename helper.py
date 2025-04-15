#!/usr/bin/env python3

import argparse
from api import Client

def main():
    parser = argparse.ArgumentParser(description="TorrServer CLI Client")
    parser.add_argument("--host", default="http://127.0.0.1:8090", help="TorrServer host")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("get_all_playlists")

    gp = subparsers.add_parser("get_playlist")
    gp.add_argument("hash", help="Torrent hash")
    gp.add_argument("--from-last", action="store_true", help="Exclude watched")

    ut = subparsers.add_parser("upload_torrent")
    ut.add_argument("path", help="Path to .torrent file")
    ut.add_argument("--title", default="", help="Torrent title")
    ut.add_argument("--poster", default="", help="Poster URL")
    ut.add_argument("--no-save", action="store_true", help="Do not save to DB")

    subparsers.add_parser("get_torrents")
    subparsers.add_parser("list_torrents")

    rt = subparsers.add_parser("remove_torrent")
    rt.add_argument("hash", help="Torrent hash")

    dt = subparsers.add_parser("drop_torrent")
    dt.add_argument("hash", help="Torrent hash")

    at = subparsers.add_parser("add_torrent")
    at.add_argument("link", help="Magnet or direct link")
    at.add_argument("--title", default="", help="Title")
    at.add_argument("--poster", default="", help="Poster")
    at.add_argument("--no-save", action="store_true", help="Do not save to DB")

    gt = subparsers.add_parser("get_torrent")
    gt.add_argument("hash", help="Torrent hash")

    args = parser.parse_args()
    client = Client(args.host)

    match args.command:
        case "get_all_playlists":
            print(client.get_all_playlists())
        case "get_playlist":
            print(client.get_playlist(args.hash, from_last=args.from_last))
        case "upload_torrent":
            result = client.upload_torrent(
                path=args.path,
                title=args.title,
                poster=args.poster,
                save_to_db=not args.no_save
            )
            print(result)
        case "get_torrents":
            print(client.get_torrents())
        case "list_torrents":
            for t in client.list_torrents():
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
            print(result)
        case "get_torrent":
            print(client.get_torrent(args.hash))
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
