import strawberry
from typing import List
from ...use_cases.song_use_case import SongUseCase
from ...repositories.song_repository import SongRepository
from ...graphql.types.song_type import Song

@strawberry.type
class Query:
    @strawberry.field
    def song(self, room_id: strawberry.auto) -> List[Song]:
        song_use_case = SongUseCase(SongRepository())
        categories = song_use_case.get_caterogies(room_id)
        return song_use_case.search_songs(categories)
    