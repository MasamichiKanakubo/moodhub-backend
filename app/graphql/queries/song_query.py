import strawberry
from typing import List
from ...use_cases.song_use_case import SongUseCase
from ...repositories.song_repository import SongRepository
from ...graphql.types.song_type import Song
import os
from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

@strawberry.type
class Query:
    @strawberry.field
    def song(self, room_id: int) -> List[Song]:
        song_use_case = SongUseCase(SongRepository(client_id, client_secret))
        categories = song_use_case.get_caterogies(room_id)
        return song_use_case.search_songs(categories)
    