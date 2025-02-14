import httpx
import uuid


async def generate_guid():
    return str(uuid.uuid4())


async def get_btn_torrents(btn_api, btn_id, meta):
    print("Fetching BTN data...")
    post_query_url = "https://api.broadcasthe.net/"
    post_data = {
        "jsonrpc": "2.0",
        "id": (await generate_guid())[:8],
        "method": "getTorrentsSearch",
        "params": [
            btn_api,
            {"id": btn_id},
            50
        ]
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(post_query_url, headers=headers, json=post_data)
        data = response.json()

    if "result" in data and "torrents" in data["result"]:
        torrents = data["result"]["torrents"]
        first_torrent = next(iter(torrents.values()), None)
        if first_torrent:
            if "ImdbID" in first_torrent:
                meta["imdb"] = first_torrent["ImdbID"]
            if "TvdbID" in first_torrent:
                meta["tvdb"] = first_torrent["TvdbID"]

    print("BTN IMDb ID:", meta.get("imdb"))
    print("BTN TVDb ID:", meta.get("tvdb"))
    return meta


async def get_bhd_torrents(bhd_api, bhd_rss_key, info_hash, meta):
    print("Fetching BHD data...")
    post_query_url = f"https://beyond-hd.me/api/torrents/{bhd_api}"
    post_data = {
        "action": "search",
        "rsskey": bhd_rss_key,
        "info_hash": info_hash,
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(post_query_url, headers=headers, json=post_data)
        data = response.json()

    if "results" in data and data["results"]:
        first_result = data["results"][0]
        imdb_id = first_result.get("imdb_id", "").replace("tt", "") if first_result.get("imdb_id") else None
        tmdb_id = first_result.get("tmdb_id", "") if first_result.get("tmdb_id") else None
        meta["imdb"] = imdb_id
        meta['category'], meta['tmdb_manual'] = await parse_tmdb_id(tmdb_id, meta.get('category'))

    print("BHD IMDb ID:", meta.get("imdb"))
    print("BHD TMDb ID:", meta.get("tmdb_manual"))
    return meta


async def parse_tmdb_id(id, category):
    id = id.lower().lstrip()
    if id.startswith('tv'):
        id = id.split('/')[1]
        category = 'TV'
    elif id.startswith('movie'):
        id = id.split('/')[1]
        category = 'MOVIE'
    else:
        id = id
    return category, id
