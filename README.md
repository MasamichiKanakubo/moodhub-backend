## MoodHub: the Track Search Engine
### Tech Stack
[![My Skills](https://skillicons.dev/icons?i=python,fastapi,mongodb,graphql,docker,gcp)](https://skillicons.dev)

## moodhub-url
This is the MoodHub backend repository.
API URL: https://mood-hub-v2.onrender.com

## Introduciton
MoodHub is a search engine for groups. You can recommend songs that everyone knows at karaoke, driving, parties, etc.
We can provide you with a comfortable musical life.

## search tracks
We use spotify API for track search.
https://developer.spotify.com/documentation/web-api

## Quick Start
### Project Environment
- Windows11
- python 3.11.3
- WSL2

### clone to your local repository
```
git clone https://github.com/MasamichiKanakubo/moodhub-backend.git
```

### install what you nedd to 
```
pip install -r requirements.txt
```

### create virtual environment and activate
```
python -m venv venv
venv\Scripts\activate
```

### setup the database
connet the MongoDB Atlas to your own app
https://www.mongodb.com/ja-jp/atlas/database

### start the app
```
uvicorn main:app --reload
```
Your app will be started with this code
