from typing import List, Optional
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL

@strawberry.type
class Song:
    song_name: str
    categories : List[str]


@strawberry.type
class Room:
    room_id: int
    user_id: List[int]
    name: str
    

@strawberry.type
class RegisterComplete:
    user_id : int
    categories : List[str]
    user_name : str
    gender : Optional[str] = None
    age : Optional[int] = None


@strawberry.input
class CreateRoom:
    user_id: int
    room_name: str


@strawberry.input
class JoinRoom:
    user_id: int
    room_id: int
    
@strawberry.input
class Register:
    user_id : int
    categories : List[str]
    user_name : str
    gender : Optional[str] = None
    age : Optional[int] = None
    
