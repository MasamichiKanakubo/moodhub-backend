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
                    self.song_categories[name].add(song_category)
        songs = [
            Song(song_name=name, categories=list(self.song_categories[name]), youtube_url=None)
            for name in self.song_categories.keys()
        ]
        songs.sort(key=lambda x: len(x.categories), reverse=True)
        sliced_songs = songs[:30]
        song_names = [song.song_name for song in sliced_songs]
        # ThreadPoolExecutorを使用してYouTube URLを非同期で取得
        with ThreadPoolExecutor() as executor:
            youtube_response = list(executor.map(
                self.song_repository.get_youtube_url, song_names))
        # 各曲にYouTube URLを設定
        for song, response in zip(sliced_songs, youtube_response):
            song.youtube_url = response["result"][0]["link"]
        return sliced_songs
