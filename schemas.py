from typing import List, Dict, Optional
import strawberry

@strawberry.type
class Song:
    song_name: str
    categories: List[str]
    track_id: str

@strawberry.type
class Room:
    room_id: int
    user_id: List[str]
    name: str
    
@strawberry.type
class Login:
    user_id: str
    
@strawberry.type
class UserDict:
    user_id: str
    avatar_url: Optional[str] = None
    
@strawberry.type
class RoomMembers:
    room_name: str
    members_dict: List[UserDict]
    

@strawberry.type
class RegisterComplete:
    user_id : str
    categories : Optional[List[str]] = None
    user_name : Optional[str] = None
    gender : Optional[str] = None
    age : Optional[int] = None
    avatar_url: Optional[str] = None


@strawberry.input
class CreateRoom:
    user_id: str
    room_name: str


@strawberry.input
class JoinRoom:
    user_id: str
    room_id: int
    
@strawberry.input
class Register:
    user_id : str
    categories : Optional[List[str]] = None
    user_name : Optional[str] = None
    gender : Optional[str] = None
    age : Optional[int] = None
    avatar_url: Optional[str] = None
    
@strawberry.input
class UpdateCategories:
    user_id: str
    categories: List[str]
    
@strawberry.input
class UpdateUserName:
    user_id: str
    user_name: Optional[str] = None
    
    
