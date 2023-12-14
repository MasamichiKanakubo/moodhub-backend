import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from typing import Union

class SongRepository:
    def __init__(self, client_id: str, client_secret: str):
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )
    
    def get_spotify_playlist(self, category: str):
        # Spotify APIを使用してプレイリストを取得
        return self.sp.search(q=category, limit=2, market="JP", type="playlist")
    
    def get_spotify_playlist_tracks(self, playlist_id: str):
        # Spotify APIを使用してプレイリストの曲を取得
        return self.sp.playlist(playlist_id=playlist_id, market="JP")

    def get_youtube_url(self, song_name: str) -> Union[str, dict]:
        # YouTube APIを使用してクエリに基づくURLを取得
        videosSearch = VideosSearch(song_name, limit = 20)
        results = videosSearch.result()
        # 結果をVideoエンティティに変換（省略）
        return results