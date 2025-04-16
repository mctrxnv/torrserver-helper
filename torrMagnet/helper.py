import argparse
from api import Client

def main():
    parser = argparse.ArgumentParser(description="TorrServer CLI Client")
    parser.add_argument("--host", default="http://127.0.0.1:8090", help="TorrServer host")

    subparsers = parser.add_subparsers(dest="command")

    at = subparsers.add_parser("add_torrent")
    at.add_argument("link", help="Magnet or direct link")
    at.add_argument("--title", default="", help="Title")
    at.add_argument("--poster", default="", help="Poster")
    at.add_argument("--no-save", action="store_true", help="Do not save to DB")

    args = parser.parse_args()
    client = Client(args.host)

    match args.command:
        case "add_torrent":
            result = client.add_torrent(
                link=args.link,
                title=args.title,
                poster=args.poster,
                save_to_db=not args.no_save
            )
            print(result)
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()

