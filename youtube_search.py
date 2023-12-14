from youtubesearchpython import VideosSearch, ChannelsSearch, PlaylistsSearch
import concurrent.futures

def youtube_search(query: str) -> dict:
    videosSearch = VideosSearch(query, limit = 500)
    results = videosSearch.result()

#youtube_searchが30回実行する時間を計測する
import time
start = time.time()
for i in range(30):
    youtube_search("夜に駈ける")
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
#elapsed_time:30.23200011253357[sec]