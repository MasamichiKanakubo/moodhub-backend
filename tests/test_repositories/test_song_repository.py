import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))
from app.repositories.song_repository import SongRepository

class TestSongRepository(unittest.TestCase):

    @patch('app.repositories.song_repository.spotipy.Spotify')
    def test_get_spotify_playlist(self, mock_spotify_class):
        # Spotifyクライアントのインスタンスをモック化
        mock_spotify_instance = MagicMock()
        mock_spotify_class.return_value = mock_spotify_instance

        # searchメソッドのレスポンスをモック化
        mock_spotify_instance.search.return_value = {
            'playlists': {'items': [{'name': 'Dummy Playlist', 'id': '123'}]}
        }

        # リポジトリのインスタンスを作成
        repo = SongRepository('dummy_client_id', 'dummy_client_secret')

        # get_spotify_playlistメソッドをテスト
        result = repo.get_spotify_playlist('rock')
        self.assertEqual(result, {
            'playlists': {'items': [{'name': 'Dummy Playlist', 'id': '123'}]}
        })

        # searchメソッドが期待通りに呼び出されたことを確認
        mock_spotify_instance.search.assert_called_once_with(
            q='rock', limit=2, market='JP', type='playlist'
        )

    @patch('app.repositories.song_repository.spotipy.Spotify')
    def test_get_spotify_playlist_tracks(self, mock_spotify_class):
        # Spotifyクライアントのインスタンスをモック化
        mock_spotify_instance = MagicMock()
        mock_spotify_class.return_value = mock_spotify_instance

        # playlistメソッドのレスポンスをモック化
        mock_spotify_instance.playlist.return_value = {
            'tracks': {'items': [{'track': {'name': 'Dummy Song'}}]}
        }

        # リポジトリのインスタンスを作成
        repo = SongRepository('dummy_client_id', 'dummy_client_secret')

        # get_spotify_playlist_tracksメソッドをテスト
        result = repo.get_spotify_playlist_tracks('123')
        self.assertEqual(result, {
            'tracks': {'items': [{'track': {'name': 'Dummy Song'}}]}
        })

        # playlistメソッドが期待通りに呼び出されたことを確認
        mock_spotify_instance.playlist.assert_called_once_with(
            playlist_id='123', market='JP'
        )

    @patch('app.repositories.song_repository.VideosSearch')
    def test_get_youtube_url(self, mock_videos_search):
        # YouTube APIのモックを設定
        mock_videos_search.return_value.result.return_value = {
            "result": [
                {
                    "type": "video",
                    "id": "K4DyBUG242c",
                    "title": "Cartoon - On & On (feat. Daniel Levi) [NCS Release]",
                    "publishedTime": "5 years ago",
                    "duration": "3:28",
                    "viewCount": {
                        "text": "389,673,774 views",
                        "short": "389M views"
                    },
                    "thumbnails": [
                        {
                            "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEjCOADEI4CSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLBkTusCwcZQlmVAaRQ5rH-mvBuA1g",
                            "width": 480,
                            "height": 270
                        }
                    ],
                    "richThumbnail": {
                        "url": "https://i.ytimg.com/an_webp/K4DyBUG242c/mqdefault_6s.webp?du=3000&sqp=COCn64IG&rs=AOn4CLBeYxeJ_5lME4jXbFQlv7kIN37kmw",
                        "width": 320,
                        "height": 180
                    },
                    "link": "https://www.youtube.com/watch?v=K4DyBUG242c",
                },
            ]
        }

        # リポジトリのインスタンスを作成
        repo = SongRepository('dummy_client_id', 'dummy_client_secret')

        # メソッドをテスト
        result = repo.get_youtube_url('夜に駆ける')
        print(result)
        self.assertEqual(result, {
            "result": [
                {
                    "type": "video",
                    "id": "K4DyBUG242c",
                    "title": "Cartoon - On & On (feat. Daniel Levi) [NCS Release]",
                    "publishedTime": "5 years ago",
                    "duration": "3:28",
                    "viewCount": {
                        "text": "389,673,774 views",
                        "short": "389M views"
                    },
                    "thumbnails": [
                        {
                            "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEjCOADEI4CSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLBkTusCwcZQlmVAaRQ5rH-mvBuA1g",
                            "width": 480,
                            "height": 270
                        }
                    ],
                    "richThumbnail": {
                        "url": "https://i.ytimg.com/an_webp/K4DyBUG242c/mqdefault_6s.webp?du=3000&sqp=COCn64IG&rs=AOn4CLBeYxeJ_5lME4jXbFQlv7kIN37kmw",
                        "width": 320,
                        "height": 180
                    },
                    "link": "https://www.youtube.com/watch?v=K4DyBUG242c",
                },
            ]
        })


if __name__ == '__main__':
    unittest.main()
