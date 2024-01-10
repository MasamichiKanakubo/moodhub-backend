import random
from app.entities.schemas import CreateRoom, JoinRoom, Room
from app.repositories.mongo_repository import MongoRepository

class RoomUseCase:
    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
        
    def add_members(self, join: JoinRoom) -> Room:
        room = self.mongo_repository.get_document(
            "RoomTable", {"room_id": join.room_id}
        )
        print(room)
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