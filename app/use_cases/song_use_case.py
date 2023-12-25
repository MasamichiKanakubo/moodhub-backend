from concurrent.futures import ThreadPoolExecutor
import os
import sys
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from app.repositories.mongo_repository import MongoRepository
from app.repositories.song_repository import SongRepository
from schemas import Song
from collections import defaultdict
from typing import List

class SongUseCase:
    def __init__(self, song_repository: SongRepository, mongo_repository: MongoRepository):
        self.song_repository = song_repository
        self.mongo_repository = mongo_repository
        self.song_categories = defaultdict(set)

    def get_categories(self, room_id: int) -> List[str]:
        room = self.mongo_repository.get_document("RoomTable", {"room_id": room_id})
        member_categories_list = []
        user_ids = room["user_id"]
        for user_id in user_ids:
            user = self.mongo_repository.get_document(
                "UserTable", {"user_id": user_id})
            if user:
                categories = user.get("categories", [])
                member_categories_list.extend(categories)
        return member_categories_list

    def search_songs(self, song_categories: List[str]) -> List[Song]:
        song_data = {}
        for song_category in song_categories:
            results = self.song_repository.get_spotify_playlist(song_category)
            # Spotifyからプレイリストを取得
            playlists = results["playlists"]["items"]
            # 各曲に対してYouTube URLを取得
            for playlist in playlists:
                playlisturl = str(playlist["href"]).split("/")
                # URLの最後の要素が欲しいので分割
                playlist_id = playlisturl[len(playlisturl) - 1]
                # URLの最後の部分がプレイリストID
                playListTrack = self.song_repository.get_spotify_playlist_tracks(playlist_id)
                for track in playListTrack["tracks"]["items"]:
                    name = track["track"]["name"]
                    track_id = track["track"]["id"]

                    if name not in song_data:
                        song_data[name] = {"categories": set(), "track_id": track_id}
                    
                    song_data[name]["categories"].add(song_category)
        songs = [
            Song(song_name=name, categories=list(info["categories"]), track_id=info["track_id"])
            for name, info in song_data.items()
        ]
        songs.sort(key=lambda x: len(x.categories), reverse=True)
        sliced_songs = songs[:30]
        
        return sliced_songs