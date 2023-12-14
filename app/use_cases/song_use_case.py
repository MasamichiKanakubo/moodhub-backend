from ..repositories.song_repository import SongRepository
from ..graphql.types.song_type import Song
from collections import defaultdict
from typing import List

class SongUseCase:
    def __init__(self, repository: SongRepository):
        self.repository = repository
        self.song_categories = defaultdict(set)
        client = MongoClient(os.environ["MONGO_URL"])
        db = client["RoomDB"]
        self.collection_room = db["RoomTable"]
        self.collection_user = db["UserTable"]

    def get_caterogies(self, room_id: int) -> List[str]:
        room = collection_room.find_one({"room_id": room_id})
        menber_categories_list = []
        user_ids = room["user_id"]
        for user_id in user_ids:
            try:
                user = collection_user.find_one({"user_id": user_id})
                categories = user["categories"]
            except TypeError:
                continue
            for category in categories:
                menber_categories_list.append(category)
        return menber_categories_list

    def search_songs(self, song_categories: List[str]) -> List[Song]:
        for song_category in song_categories:
            self.repository.get_spotify_playlist(song_category)
            # Spotifyからプレイリストを取得
            playlists = results["playlists"]["items"]
            # 各曲に対してYouTube URLを取得
            for playlist in playlists:
                playlisturl = str(playlist["href"]).split("/")
                # URLの最後の要素が欲しいので分割
                playlist_id = playlisturl[len(playlisturl) - 1]
                # URLの最後の部分がプレイリストID
                playListTrack = self.repository.get_spotify_playlist_tracks(playlist_id)
                for track in playListTrack["tracks"]["items"]:
                    name = track["track"]["name"]
                    self.song_categories[name].add(category_name)
        songs = [
            Song(song_name=name, categories=list(song_categories[name]))
            for name in song_categories.keys()
        ]
        songs.sort(key=lambda x: len(x.categories), reverse=True)
        sliced_song = songs[:30]
        with ThreadPoolExecutor() as executor:
            results = executor.map(self.repository.search, queries)
        for sliced_song, i in enumerate(sliced_songs):
            sliced_song.url = results[i]
        return list(results)
