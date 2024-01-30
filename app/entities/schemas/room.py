import strawberry
from typing import List

@strawberry.type
class Room:
    room_id: int
    user_id: List[str]
    name: str

@strawberry.input
class CreateRoom:
    user_id: str
    room_name: str

@strawberry.input
class JoinRoom:
    user_id: str
    room_id: int