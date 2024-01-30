import random
from app.entities.schemas.room import Room, CreateRoom, JoinRoom
from app.repositories.mongo_repository import MongoRepository

# Roomに関連するユースケースをまとめた。
# 単一責任の原則は自分の解釈では一つのファイルで一つの役割をもつと思ったのでここではルームに関する機能だけを取り扱った
# ユースケース層はentities層とrepositories層にのみ依存しているように設計
class RoomUseCase:
    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
    
    def add_members(self, join: JoinRoom) -> Room:
        room = self.mongo_repository.get_document(
            "RoomTable", {"room_id": join.room_id}
        )
        if join.user_id in room["user_id"]:
            return Room(room_id=room["room_id"], user_id=room["user_id"], name=room["name"])
        
        self.mongo_repository.push_document(
            "RoomTable",
            {"room_id": join.room_id},
            {"user_id": join.user_id}
        )
        room = self.mongo_repository.get_document(
            "RoomTable", {"room_id": join.room_id}
        )
        return Room(room_id=room["room_id"], user_id=room["user_id"], name=room["name"])
    
    def get_new_room(self, room: CreateRoom) -> Room:
        new_room = Room(
            room_id=random.randint(1, 100000),
            user_id=[room.user_id],
            name=room.room_name
        )
        self.mongo_repository.insert_document(
            "RoomTable", new_room.__dict__
        )
        return new_room