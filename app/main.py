import os
from typing import List
from dotenv import load_dotenv
import asyncio
import aiohttp
import strawberry
from strawberry.asgi import GraphQL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from spotipy.oauth2 import SpotifyClientCredentials
from app.entities.schemas.song import Song
from app.entities.schemas.room import Room, CreateRoom, JoinRoom
from app.entities.schemas.user import Register, RegisterComplete, RoomMembers, UpdateUserName, UpdateCategories
from app.repositories.mongo_repository import MongoRepository
from app.repositories.song_repository import SongRepository
from app.use_cases.song_use_case import SongUseCase
from app.use_cases.user_data_use_case import UserDataUseCase
from app.use_cases.room_use_case import RoomUseCase

load_dotenv()

# リポジトリのインスタンスを作成
mongo_repository = MongoRepository(client=MongoClient(os.environ.get("MONGO_URI")), db_name="RoomDB")
song_repository = SongRepository(
    client_credentials=SpotifyClientCredentials(
        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET')
    ))

# ユースケースのインスタンスを作成
user_data_use_case = UserDataUseCase(mongo_repository)
room_use_case = RoomUseCase(mongo_repository)

@strawberry.type
class Query:
    @strawberry.field
    def song(self, room_id: int) -> List[Song]:
        song_use_case = SongUseCase(song_repository, mongo_repository)
        categories = song_use_case.get_categories(room_id)
        return song_use_case.search_songs(categories)
    
    @strawberry.field
    def get_user_info(self, user_id: str) -> RegisterComplete:
        return user_data_use_case.show_personal_info(user_id)

    @strawberry.field
    def get_members(self, room_id: int) -> RoomMembers:
        return user_data_use_case.show_room_members_info(room_id)

@strawberry.type
class Mutation:
    @strawberry.field
    def create_room(self, room: CreateRoom) -> Room:
        return room_use_case.get_new_room(room)
        
    @strawberry.field
    def join_room(self, join: JoinRoom) -> Room:
        return room_use_case.add_members(join)
        
    @strawberry.field
    def register(self, regist: Register) -> RegisterComplete:
        return user_data_use_case.sign_up(regist)
    
    @strawberry.field
    def update_category(self, update: UpdateCategories) -> RegisterComplete:
        return user_data_use_case.set_new_categories(update)

    @strawberry.field
    def update_username(self, update: UpdateUserName) -> RegisterComplete:
        return user_data_use_case.set_new_username(update)


schema = strawberry.Schema(query=Query, mutation=Mutation)

sdl = str(schema)

with open("app/entities/graphql/schema.graphql", "w") as f:
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

