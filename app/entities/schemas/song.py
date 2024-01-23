from typing import List
import strawberry

@strawberry.type
class Song:
    song_name: str
    categories: List[str]
    track_id: str    
    