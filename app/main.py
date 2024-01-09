import os
from pymongo import MongoClient, errors
from typing import List
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware
import random
from app.entities.schemas import (Song, Room, RegisterComplete, CreateRoom,
                     JoinRoom, Register, UpdateCategories, RoomMembers, UpdateUserName, UserDict)
import asyncio
import aiohttp
from app.repositories.mongo_repository import MongoRepository
from app.use_cases.song_use_case import SongUseCase
from app.repositories.song_repository import SongRepository

load_dotenv()

# リポジトリのインスタンスを作成
mongo_repo = MongoRepository(uri=os.environ["MONGO_URL"], db_name="RoomDB")
song_repo = SongRepository(
    client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"])

client = MongoClient(os.environ["MONGO_URL"])
db = client["RoomDB"]
collection_room = db["RoomTable"]
collection_user = db["UserTable"]

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
)


@strawberry.type
class Query:
    @strawberry.field
    def song(self, room_id: int) -> List[Song]:
        song_use_case = SongUseCase(song_repo, mongo_repo)
        categories = song_use_case.get_categories(room_id)
        return song_use_case.search_songs(categories)
    
    @strawberry.field
    def get_user_info(self, user_id: str) -> RegisterComplete:
        try:
            user = collection_user.find_one(filter={"user_id": user_id})
            user_name = user["user_name"]
            user_categories = user["categories"]
            avatar_url = user["avatar_url"]
            return RegisterComplete(
                user_id=user_id, user_name=user_name, categories=user_categories, avatar_url=avatar_url
            )
        except TypeError:
            return Exception("エラー")

    @strawberry.field
    def get_members(self, room_id: int) -> RoomMembers:
        room = collection_room.find_one(filter={"room_id": room_id})
        user_ids = room["user_id"]

        members_list = []
        for user_id in user_ids:
            user = collection_user.find_one(filter={"user_id": user_id})
            user_id = user["user_id"]
            avatar_url = user["avatar_url"]
            user_dict = UserDict(user_id=user_id, avatar_url=avatar_url)
            members_list.append(user_dict)
        return RoomMembers(room_name=room["name"], members_dict=members_list)


async def schedule_room_deletion(room_id):
    # 24時間後にルームを削除
    await asyncio.sleep(86400)
    collection_room.delete_one({"room_id": room_id})


async def schedule_user_deletion(user_id):
    await asyncio.sleep(86400)
    collection_user.delete_one({"user_id": user_id})


@strawberry.type
class Mutation:
    @strawberry.field
    async def create_room(self, room: CreateRoom) -> Room:
        new_room = Room(
            room_id=random.randint(1, 100000),
            user_id=[room.user_id],
            name=room.room_name,
        )
        collection_room.insert_one(new_room.__dict__)
        asyncio.create_task(schedule_room_deletion(new_room.room_id))
        return new_room

    @strawberry.field
    def join_room(self, join: JoinRoom) -> Room:
        existing_user = collection_room.find_one(
            {"room_id": join.room_id, "user_id": {
                "$elemMatch": {"$eq": join.user_id}}}
        )

        if existing_user:
            raise ValueError('You are already in the room')

        collection_room.update_one(
            {"room_id": join.room_id}, {"$push": {"user_id": join.user_id}}
        )
        room = collection_room.find_one(filter={"room_id": join.room_id})
        return Room(room_id=room["room_id"], user_id=room["user_id"], name=room["name"])

    @strawberry.field
    def update_category(self, update: UpdateCategories) -> RegisterComplete:
        collection_user.update_one(
            {"user_id": update.user_id},
            {"$set": {"categories": update.categories}},
        )
        user = collection_user.find_one(filter={"user_id": update.user_id})
        return RegisterComplete(
            user_id=user["user_id"],
            categories=user["categories"],
            user_name=user["user_name"],
            avatar_url=user["avatar_url"]
        )

    @strawberry.field
    def register(self, regist: Register) -> RegisterComplete:
        try:
            collection_user.insert_one(regist.__dict__)
            asyncio.create_task(schedule_user_deletion(regist.user_id))
            return regist 
        except errors.DuplicateKeyError:
            raise Exception("You are already registered with MoodHub")
        except Exception as e:
            raise {"message": str(e)}
        
    @strawberry.field
    def update_username(self, update: UpdateUserName) -> RegisterComplete:
        user = collection_user.find_one(filter={'user_id': update.user_id})
        collection_user.update_one(
            {'user_id': update.user_id},
            {'$set': {'user_name': update.user_name}},
        )
        return RegisterComplete(
            user_id=user['user_id'],
            user_name=user['user_name']
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)

sdl = str(schema)

with open("app/interfaces/schema.graphql", "w") as f:
    f.write(sdl)

graphql_app = GraphQL(schema)


app = FastAPI()

deploy_url = "https://mood-hub-v2.onrender.com"

app.add_route("/graphql", graphql_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def send_request():
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(deploy_url) as response:
                print(await response.text())
        await asyncio.sleep(60)  # 60秒ごとにリクエストを送信


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_request())


@app.get("/")
async def root():
    return {"message": "Hello World"}

