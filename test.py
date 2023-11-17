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


load_dotenv()

client = MongoClient(os.environ["MONGO_URL"])
db = client["RoomDB"]


client_id = os.getenv('CLIENT_ID') 
client_secret = os.getenv('CLIENT_SECRET')

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
)

results = sp.search(q="ひげだん", limit=10, market='JP', type="track")
for track in results['tracks']['items']:
    name = track['name']
    track_id = track['id']
    track_info = sp.audio_features(track_id)
    bpm = track_info[0]['tempo']
    print(f'{name} : {bpm}')

