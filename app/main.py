import os
from typing import List
from dotenv import load_dotenv
import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import asyncio
import aiohttp
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
mongo_repo = MongoRepository(uri=os.environ.get("MONGO_URL"), db_name="RoomDB")
song_repo = SongRepository(client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"])

# ユースケースのインスタンスを作成
user_data_use_case = UserDataUseCase(mongo_repo)
room_use_case = RoomUseCase(mongo_repo)

@strawberry.type
class Query:
    # mainはエントリーポイントだからロジック自体を別で行いリクエストに対するレスポンスだけを表示する意味で書いた
    @strawberry.field
    def song(self, room_id: int) -> List[Song]:
        song_use_case = SongUseCase(song_repo, mongo_repo)
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
    # ロジックをとにかく書かないことを意識した。なんならここにMutationやQueryを書くこともおかしいんじゃないかという気もする
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

# この部分ファイルが実行されるとちゃんと書き換わるがここにかいているのが若干違和感ある
# ここである必要性を感じないというかエントリーポイントでやるべきなのか疑問
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


# この処理はrenderやホスティングプラットフォームでCRONで書き直すか検討中。CRONで定期実行するのと差がない気がしている
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

