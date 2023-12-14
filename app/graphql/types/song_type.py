import strawberry
from typing import List

@strawberry.type
class Song:
    song_name: str
    categories: List[str]
    youtube_url: str