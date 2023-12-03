import os
from pymongo import MongoClient
from typing import List
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware
import random
from collections import defaultdict
from schemas import (Song, Room, RegisterComplete, CreateRoom, JoinRoom, Register, UpdateCategories, RoomMembers, UpdateUserName)
import asyncio
import aiohttp
import redis

load_dotenv()

redis_client = redis.Redis(
  host=os.getenv('REDIS_HOST'),
  port=os.getenv('REDIS_PORT'),
  password=os.getenv('REDIS_PASSWORD'),
  ssl=True
)

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
        room = collection_room.find_one({"room_id": room_id})
        # print(room)
        menber_categories_list = []

        user_ids = room["user_id"]

        for user_id in user_ids:
            try:
                user = collection_user.find_one({"user_id": user_id})
                categories = user["categories"]
            except TypeError:
                continue
            for category in categories:
                menber_categories_list.append(category)

        song_categories = defaultdict(set)

        for category_name in menber_categories_list:
            results = sp.search(q=category_name, limit=2, market="JP", type="playlist")
            # 同じプレイリストIDはskipする
            # グローバル変数にプレイリストIDごとに検索結果を保存しておいて、2回目以降ば変数からデータを取得する
            for playlist in results["playlists"]["items"]:
                playlisturl = str(playlist["href"]).split("/")
                # URLの最後の要素が欲しいので分割
                playlistID = playlisturl[len(playlisturl) - 1]
                # URLの最後の部分がプレイリストID
                playListTrack = sp.playlist(playlist_id=playlistID, market="JP")

                for track in playListTrack["tracks"]["items"]:
                    name = track["track"]["name"]
                    song_categories[name].add(category_name)

        songs = [
            Song(song_name=name, categories=list(song_categories[name]))
            for name in song_categories.keys()
        ]

        songs.sort(key=lambda x: len(x.categories), reverse=True)
        sliced_song = songs[:30]

        return sliced_song

    @strawberry.field
    def get_members(self, room_id: int) -> RoomMembers:
        room = collection_room.find_one(filter={"room_id": room_id})
        user_ids = room["user_id"]

        user_names = []
        for user_id in user_ids:
            user = collection_user.find_one(filter={"user_id": user_id})
            user_name = user["user_name"]
            user_names.append(user_name)
        return RoomMembers(room_name=room["name"], members=user_names)

    @strawberry.field
    def get_user_info(self, user_id: int) -> RegisterComplete:
        try:
            user = collection_user.find_one(filter={"user_id": user_id})
            user_name = user["user_name"]
            user_categories = user["categories"]
            return RegisterComplete(
                user_id=user_id, user_name=user_name, categories=user_categories
            )
        except TypeError:
            return Exception("エラー")

    @strawberry.field
    def get_members(self, room_id: int) -> RoomMembers:
        room = collection_room.find_one(filter={"room_id": room_id})
        user_ids = room["user_id"]

        user_names = []
        for user_id in user_ids:
            user = collection_user.find_one(filter={"user_id": user_id})
            user_name = user["user_name"]
            user_names.append(user_name)
        return RoomMembers(room_name=room["name"], members=user_names)


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
            {"room_id": join.room_id, "user_id": {"$elemMatch": {"$eq": join.user_id}}}
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
        )

    @strawberry.field
    def register(self, regist: Register) -> RegisterComplete:
        collection_user.insert_one(regist.__dict__)
        asyncio.create_task(schedule_user_deletion(regist.user_id))
        return regist
    
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

with open("schema.graphql", "w") as f:
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
