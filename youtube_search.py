from youtubesearchpython import VideosSearch, ChannelsSearch, PlaylistsSearch

def youtube_search(query: str) -> dict:
    videosSearch = VideosSearch(query, limit = 500)
    results = videosSearch.result()
