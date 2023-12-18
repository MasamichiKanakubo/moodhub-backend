import unittest
from unittest.mock import patch, MagicMock
from app.use_cases.song_use_case import SongUseCase
from app.repositories.mongo_repository import MongoRepository
from app.repositories.song_repository import SongRepository


class TestSongUseCase(unittest.TestCase):

    @patch('app.repositories.mongo_repository.MongoRepository')
    @patch('app.repositories.song_repository.SongRepository')
    def setUp(self, mock_song_repo, mock_mongo_repo):
        self.mock_song_repo = mock_song_repo.return_value
        self.mock_mongo_repo = mock_mongo_repo.return_value
        self.song_use_case = SongUseCase(
            self.mock_song_repo, self.mock_mongo_repo)

    def test_get_categories(self):
        self.mock_mongo_repo.get_document.return_value = {
            "user_id": [1, 2]
        }
        self.mock_mongo_repo.get_document.side_effect = [
            {
                "user_id": [1, 2]
            },
            {"categories": ["平成", "アニソン"]},
            {"categories": ["pop"]},
        ]

        categories = self.song_use_case.get_categories(1)
        self.assertEqual(categories, ["平成", "アニソン", "pop"])

    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_search_songs(self, mock_executor):
        self.mock_song_repo.get_spotify_playlist.return_value = {
            "playlists": {"items": [{"href": "https://example.com/123"}]}}
        self.mock_song_repo.get_spotify_playlist_tracks.return_value = {
            "tracks": {"items": [
                {
                    "track": {
                        "name": "Dummy Song",
                        "artists": [{"name": "Dummy Artist"}]
                    }
                },
                {
                    "track": {
                        "name": "Dummy Song2",
                        "artists": [{"name": "Dummy Artist2"}]
                    }
                },
            ]}}
        mock_executor.return_value.__enter__.return_value.map.return_value = [
            {}]

        songs = self.song_use_case.search_songs(["rock"])
        self.assertIsInstance(songs, list)
