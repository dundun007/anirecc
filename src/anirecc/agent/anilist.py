import requests
import time
import difflib
from functools import lru_cache

ANILIST_API_URL = "https://graphql.anilist.co"

# Fetches a user's AniList anime activity from the past 7 days.
def get_recent_anilist_anime(username: str) -> list[dict]:
    print(f"DEBUG: Agent fetching recent anime activity for {username} on AniList...")
    lists = fetch_anilist_user_list(username, "ANIME")
    
    recent_activity = []
    seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
    
    for anime_list in lists:
        entries = anime_list.get("entries", [])
        for entry in entries:
            if entry.get("updatedAt", 0) >= seven_days_ago and entry.get("status") in ["CURRENT", "COMPLETED"]:
                title = entry["media"]["title"].get("english") or entry["media"]["title"].get("romaji")
                
                recent_activity.append({
                    "title": title,
                    "genres": entry["media"].get("genres", []),
                    "status": entry.get("status"),
                })
            
    return recent_activity

# Fetches a user's AniList manga activity from the past 7 days.
def get_recent_anilist_manga(username: str) -> list[dict]:
    print(f"DEBUG: Agent fetching recent manga activity for {username} on AniList...")
    lists = fetch_anilist_user_list(username, "MANGA")
    
    recent_activity = []
    seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
    
    for anime_list in lists:
        entries = anime_list.get("entries", [])
        for entry in entries:
            if entry.get("updatedAt", 0) >= seven_days_ago and entry.get("status") in ["CURRENT", "COMPLETED"]:
                title = entry["media"]["title"].get("english") or entry["media"]["title"].get("romaji")
                
                recent_activity.append({
                    "title": title,
                    "genres": entry["media"].get("genres", []),
                    "status": entry.get("status"),
                })
            
    return recent_activity

# Fetches a user's entire AniList manga/anime collection
@lru_cache(maxsize=32)
def fetch_anilist_user_list(username: str, media_type: str) -> list:
    graphql_query = """
    query ($userName: String, $mediaType: MediaType) {
        MediaListCollection(userName: $userName, type: $mediaType) {
            lists {
                entries {
                    media {
                        title { 
                            romaji 
                            english 
                        }
                        synonyms
                        genres
                    }
                    status
                    updatedAt
                }
            }
        }
    }
    """

    variables = {
        "userName": username,
        "mediaType": media_type.upper()
    }

    for attempt in range(3):
        try:
            response = requests.post(ANILIST_API_URL, json={'query': graphql_query, 'variables': variables})
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("MediaListCollection", {}).get("lists", [])
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else None
            print(f"DEBUG: AniList API Error {status_code}. Retrying ({attempt+1}/3)...")
            if status_code == 429:
                time.sleep(5)
            else:
                time.sleep(2)
            
    print("DEBUG: AniList API failed after 3 retries. Returning empty list as fallback.")
    return []

# Checks if a title exists in the user's AniList.
def check_anilist_title_in_user_list(username: str, title: str, media_type: str) -> bool:
    print(f"DEBUG: Agent checking if '{title}' is in {username}'s list...")
    lists = fetch_anilist_user_list(username, media_type)

    search_title = title.lower()

    for anime_list in lists: 
        for entry in anime_list.get("entries", []):
            title_dict = entry["media"]["title"]
            
            all_titles = []
            if title_dict.get("romaji"): all_titles.append(title_dict.get("romaji"))
            if title_dict.get("english"): all_titles.append(title_dict.get("english"))
            
            synonyms = entry["media"].get("synonyms", [])
            if synonyms: 
                all_titles.extend(synonyms)

            for t in all_titles:
                t_lower = t.lower()
                if difflib.SequenceMatcher(None, search_title, t_lower).ratio() > 0.7 or search_title in t_lower:
                    return True

    return False
        

# Verifies if a title exists on AniList.
def verify_title_exists_on_anilist(title: str, media_type: str) -> str:
    print(f"DEBUG: Agent verifying if '{title}' actually exists on AniList...")

    graphql_query = """
    query ($search: String, $type: MediaType) {
        Media(search: $search, type: $type) {
            id
            siteUrl
            title {
                romaji
                english
            }
        }
    }
    """

    variables = {
        "search": title,
        "type": media_type.upper()
    }

    try:
        response = requests.post(ANILIST_API_URL, json={'query': graphql_query, 'variables': variables})
        response.raise_for_status()
        data = response.json()

        media = data.get("data", {}).get("Media", {})
        
        if media:
            info = {
                "id": media.get("id"),
                "url": f"https://anilist.co/{media_type.lower()}/{media.get('id')}",
                "official_title": media["title"].get("english") or media["title"].get("romaji")
            }
            return str(info)
        
        return "Not found"
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying AniList API: {e}")
        return "Not found"
