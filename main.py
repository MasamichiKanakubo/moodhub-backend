import os
from pymongo import MongoClient
from typing import List
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import strawberry
from fastapi import FastAPI, BackgroundTasks, Depends
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware
import random
from collections import defaultdict
from schemas import Song, Room, RegisterComplete, CreateRoom, JoinRoom, Register
import asyncio
import aiohttp
# github確認
load_dotenv()

client = MongoClient(os.environ["MONGO_URL"])
db = client["RoomDB"]

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
        room = db["RoomTable"].find_one({'room_id':room_id})
        # print(room)
        menber_categories_list = []
        
        user_ids = room["user_id"]
        
        for user_id in user_ids:
            try:
                user = db["UserTable"].find_one({"user_id":user_id})
                categories = user["categories"]
            except TypeError:
                continue
            for c in categories:
                menber_categories_list.append(c)
            

        song_categories = defaultdict(set)  

        for k in menber_categories_list:
            results = sp.search(q=k, limit=3, market="JP", type="playlist")

            for idx, playlist in enumerate(results["playlists"]["items"]):
                playlisturl = str(playlist["href"]).split("/")
                # URLの最後の要素が欲しいので分割
                playlistID = playlisturl[len(playlisturl)-1]
                # URLの最後の部分がプレイリストID
                playListTrack = sp.playlist(playlist_id=playlistID, market="JP")

                for i, track in enumerate(playListTrack["tracks"]["items"]):
                    name = track["track"]["name"]
                    song_categories[name].add(k)  

        songs = [Song(song_name=name, categories=list(song_categories[name])) for name in song_categories.keys()]

        songs.sort(key=lambda x: len(x.categories), reverse=True)
        sliced_song = songs[:30]
                
        return sliced_song


async def schedule_room_deletion(room_id):
    # 24時間後にルームを削除
    await asyncio.sleep(86400)  
    collection = db["RoomTable"]
    collection.delete_one({"room_id": room_id})

async def schedule_user_deletion(user_id):
    await asyncio.sleep(86400)
    collection = db["UserTable"]
    collection.delete_one({"user_id": user_id})
    
@strawberry.type
class Mutation:
    @strawberry.field
    async def create_room(self, room: CreateRoom) -> Room:
        new_room = Room(
            room_id=random.randint(1, 100000),
            user_id=[room.user_id],
            name=room.room_name,
        )
        collection = db["RoomTable"]
        collection.insert_one(new_room.__dict__)
        asyncio.create_task(schedule_room_deletion(new_room.room_id))
        return new_room

    @strawberry.field
    def join_room(self, join: JoinRoom) -> Room:
        collection = db["RoomTable"]
        collection.update_one(
            {"room_id": join.room_id}, {"$push": {"user_id": join.user_id}}
        )
        room = collection.find_one(filter={"room_id": join.room_id})
        return Room(room_id=room["room_id"], user_id=room["user_id"], name=room["name"])
    

    @strawberry.field
    def register(self, regist:Register) -> RegisterComplete:
        collection = db["UserTable"]
        collection.insert_one(regist.__dict__)
        asyncio.create_task(schedule_user_deletion(regist.user_id))
        return regist


schema = strawberry.Schema(query=Query, mutation=Mutation)

sdl = str(schema)

with open("schema.graphql", "w") as f:
    f.write(sdl)

graphql_app = GraphQL(schema)


app = FastAPI()

deploy_url = 'https://mood-hub-v2.onrender.com'

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
