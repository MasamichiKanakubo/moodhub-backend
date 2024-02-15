from app.entities.schemas.user import (
    Register, RegisterComplete, UserDict, RoomMembers, UpdateUserName, UpdateCategories, UpdateAvatar, TextMessage
    )
from app.repositories.mongo_repository import MongoRepository
from pymongo import errors

class UserDataUseCase:
    def __init__(self, mongo_repository: MongoRepository):
        self.mongo_repository = mongo_repository
        
    def show_room_members_info(self, room_id: int) -> RoomMembers:
        room = self.mongo_repository.get_document(
            "RoomTable", {"room_id": room_id}
        )
        user_ids = room["user_id"]
        
        members_info_list: list = []
        for user_id in user_ids:
            user = self.mongo_repository.get_document(
                "UserTable", {"user_id": user_id}
            )
            user_dict = UserDict(
                user_id=user_id,
                avatar_url=user["avatar_url"],
            )
            members_info_list.append(user_dict)
        return RoomMembers(room_name=room["name"], members_info_list=members_info_list)
    
    def show_personal_info(self, user_id: str) -> RegisterComplete:
        try:
            user = self.mongo_repository.get_document(
                "UserTable", {"user_id": user_id}
            )
            user_name = user["user_name"]
            avatar_url = user["avatar_url"]
            return RegisterComplete(
                user_id=user_id, user_name=user_name, avatar_url=avatar_url
            )
        except TypeError:
            raise Exception("This user does not exist.")
        
    def sign_up(self, regist: Register) -> RegisterComplete:
        try:
            self.mongo_repository.insert_document(
                "UserTable", regist.__dict__
            )
            return regist
        except errors.DuplicateKeyError:
            raise Exception('You are already registered with Moodhub')
        except Exception as e:
            raise {"message": str(e)}
        
    def set_new_username(self, update: UpdateUserName) -> RegisterComplete:
        user = self.mongo_repository.get_document(
            "UserTable", {"user_id": update.user_id}
        )
        self.mongo_repository.set_document(
            "UserTable",
            {"user_id": user["user_id"]},
            {"user_name": update.user_name}
        )
        return RegisterComplete(
            user_id=user["user_id"],
            user_name=user["user_name"]
        )
        
    def set_new_categories(self, update: UpdateCategories) -> RegisterComplete:
        self.mongo_repository.set_document(
            "UserTable",
            {"user_id": update.user_id},
            {"categories": update.categories}
        )
        user = self.mongo_repository.get_document(
            "UserTable",
            {"user_id": update.user_id}
        )
        return RegisterComplete(
            user_id=user["user_id"],
            user_name=user["user_name"],
            categories=user["categories"],
        )
    
    def set_new_avatar(self, update: UpdateAvatar) -> RegisterComplete:
        self.mongo_repository.set_document(
            "UserTable",
            {"user_id": update.user_id},
            {"avatar_url": update.avatar_url}
        )
        return RegisterComplete(
            user_id=update.user_id,
            avatar_url=update.avatar_url
        )
        
    def remove_user_info(self, user_id: str) -> TextMessage:
        self.mongo_repository.delete_document(
            "UserTable", {"user_id": user_id}
        )
        return TextMessage(message=f"user_id: {user_id} has been deleted successfully.")
