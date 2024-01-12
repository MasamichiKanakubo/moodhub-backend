from typing import List, Optional
import strawberry

# エンティティ層はプロジェクトのコアコンセプトで一番内側である必要がある、つまりほかのどのfileにも依存していな必要があると解釈した
# ビジネスロジックというのがModelに相当するので、ここではモデルにあたるスキーマのファイルを配置している
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
    
# 個々の部分ロジックとしては正しいのですが、本当にこの書き方でいいのか不安
# 下記のRoomMembersスキーマでルームメンバーのユーザ情報を返す用だがこれを経由して書いているのが若干違和感ある
@strawberry.type
class UserDict:
    user_id: str
    avatar_url: Optional[str] = None
    
@strawberry.type
class RoomMembers:
    room_name: str
    members_info_list: List[UserDict]
    
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
    
# ユーザID以外はあとから更新できるようにする、いつでも編集可能であるほうが利便性がよいと思いOptional型にしている
@strawberry.input
class Register:
    user_id : str
    categories : Optional[List[str]] = None
    user_name : Optional[str] = None
    gender : Optional[str] = None
    age : Optional[int] = None
    avatar_url: Optional[str] = None
    

# Updateは更新する物自体がそこまで多くないが一アクションに対して一つ更新される方が自然だと感じた
# カテゴリの更新はこの段階でカテゴリ以外に更新するものがないのとカテゴリの更新をのちのちトリガーにしたくもある
@strawberry.input
class UpdateCategories:
    user_id: str
    categories: List[str]
    
# 名前は誰とカラオケに行くかによって変更したいと思う
@strawberry.input
class UpdateUserName:
    user_id: str
    user_name: Optional[str] = None   
    