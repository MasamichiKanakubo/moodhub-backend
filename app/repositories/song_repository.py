from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

class SongRepository:
    def __init__(self, client_credentials: SpotifyClientCredentials):
        self.spotify_client = Spotify(auth_manager=client_credentials)
    
    def get_spotify_playlist(self, category: str):
        # Spotify APIを使用してプレイリストを取得
        return self.spotify_client.search(q=category, limit=3, market="JP", type="playlist")
    
    def get_spotify_playlist_tracks(self, playlist_id: str):
        # Spotify APIを使用してプレイリストの曲を取得
        return self.spotify_client.playlist(playlist_id=playlist_id, market="JP")
