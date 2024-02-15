import strawberry
from typing import List, Optional

@strawberry.type
class RegisterComplete:
    user_id : str
    categories : Optional[List[str]] = None
    user_name : Optional[str] = None
    gender : Optional[str] = None
    age : Optional[int] = None
    avatar_url: Optional[str] = None

@strawberry.type
class UserDict:
    user_id: str
    avatar_url: Optional[str] = None
    
@strawberry.type
class RoomMembers:
    room_name: str
    members_info_list: List[UserDict]
    
@strawberry.type
class TextMessage:
    message: str

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
    
@strawberry.input
class UpdateAvatar:
    user_id: str
    avatar_url: str
    

    