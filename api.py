import json
from dataclasses import dataclass
from datetime import datetime
import requests

@dataclass
class File:
    id: int
    path: str
    length: int

@dataclass
class Torrent:
    title: str
    poster: str
    files: list[File]
    date: datetime
    hash: str
    torrent_size: int

class BaseAPI:
    def __init__(self, host: str) -> None:
        self._host = host.rstrip('/')

    def _get(self, url: str, **kwargs) -> requests.Response:
        return requests.get(f"{self._host}/{url}", **kwargs)

    def _post(self, url: str, **kwargs) -> requests.Response:
        return requests.post(f"{self._host}/{url}", **kwargs)

class SettingsAPI(BaseAPI):
    def get_settings(self) -> dict:
        json_data = {"action": "get"}
        return self._post("settings", json=json_data).json()

class ServerAPI(BaseAPI):
    def echo(self) -> str:
        return self._get("echo").text

    def shutdown(self) -> str:
        return self._get("shutdown").text

class PlaylistAPI(BaseAPI):
    def get_all_playlists(self) -> str:
        return self._get("playlistall/all.m3u").text

    def get_playlist(self, torrent_hash: str, from_last: bool = False) -> str:
        params = {"hash": torrent_hash}
        if from_last:
            params["fromlast"] = "true"
        return self._get("playlist", params=params).text

class TorrentAPI(BaseAPI):
    def upload_torrent(self, path: str, title: str = "", poster: str = "", save_to_db: bool = True) -> dict:
        data = {"title": title, "poster": poster, "save": str(save_to_db).lower()}
        with open(path, "rb") as file:
            files_data = {"file": file}
            return self._post("torrent/upload", data=data, files=files_data).json()

    def get_torrents(self) -> list[dict]:
        json_data = {"action": "list"}
        return self._post("torrents", json=json_data).json()

    def remove_torrent(self, torrent_hash: str) -> str:
        json_data = {"action": "rem", "hash": torrent_hash}
        return self._post("torrents", json=json_data).text

    def drop_torrent(self, torrent_hash: str) -> str:
        json_data = {"action": "drop", "hash": torrent_hash}
        return self._post("torrents", json=json_data).text

    def add_torrent(self, link: str, title: str = "", poster: str = "", save_to_db: bool = True) -> dict:
        json_data = {
            "action": "add",
            "link": link,
            "title": title,
            "poster": poster,
            "save_to_db": save_to_db,
        }
        return self._post("torrents", json=json_data).json()

    def set_torrent(self, torrent_hash: str, title: str = None, poster: str = None) -> str:
        json_data = {
            "action": "set",
            "hash": torrent_hash,
        }
        if title is not None:
            json_data["title"] = title
        if poster is not None:
            json_data["poster"] = poster
        return self._post("torrents", json=json_data).text

    def get_cache(self, torrent_hash: str) -> dict:
        json_data = {"action": "get", "hash": torrent_hash}
        return self._post("cache", json=json_data).json()

    def get_torrent(self, torrent_hash: str) -> dict:
        json_data = {"action": "get", "hash": torrent_hash}
        return self._post("torrents", json=json_data).json()

class Client(ServerAPI, SettingsAPI, PlaylistAPI, TorrentAPI):
    def list_torrents(self) -> list[Torrent]:
        torrents_data = self.get_torrents()
        torrents = []
        for torrent_dict in torrents_data:
            try:
                data = json.loads(torrent_dict.get("data", "{}"))
                files_info = data.get("TorrServer", {}).get("Files", [])
                files = [File(**file_dict) for file_dict in files_info]
                torrent = Torrent(
                    title=torrent_dict.get("title", ""),
                    poster=torrent_dict.get("poster", ""),
                    files=files,
                    date=datetime.fromtimestamp(torrent_dict.get("timestamp", 0)),
                    hash=torrent_dict.get("hash", ""),
                    torrent_size=torrent_dict.get("torrent_size", 0),
                )
                torrents.append(torrent)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Log or handle the error as needed
                continue
        return torrents

