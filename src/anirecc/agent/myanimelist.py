import requests
import time
import os
import difflib
from functools import lru_cache
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
MAL_CLIENT_ID = os.getenv("MAL_CLIENT_ID")

# Fetches a user's MyAnimeList anime activity from the past 7 days.
def get_recent_myanimelist_anime(username: str) -> list[dict]:
    print(f"DEBUG: Agent fetching recent anime activity for {username} on MyAnimeList...")
    mal_api_url = f"https://api.myanimelist.net/v2/users/{username}/animelist"

    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }
    
    params = {
        "fields": "list_status, genres",
        "sort": "list_updated_at",
        "limit": 50
    }

    try:
        response = requests.get(mal_api_url, headers=headers, params = params)
        response.raise_for_status()
        data = response.json()
        
        recent_activity = []

        seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
        
        for item in data.get("data", []):
            node = item.get("node", {})
            list_status = item.get("list_status", {})

            updated_str = list_status.get("updated_at")
            
            if updated_str:
                updated_at = datetime.fromisoformat(updated_str).timestamp()

                if updated_at >= seven_days_ago and list_status.get("status") in ["watching", "completed"]:
                    recent_activity.append({
                        "title" : node.get("title"),
                        "genres": [g.get("name") for g in node.get("genres", [])],
                        "status" : list_status.get("status")
                    })
            
        return recent_activity
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying MyAnimeList API: {e}")
        return []

# Fetches a user's MyAnimeList manga activity from the past 7 days.
def get_recent_myanimelist_manga(username: str) -> list[dict]:
    print(f"DEBUG: Agent fetching recent manga activity for {username} on MyAnimeList...")
    mal_api_url = f"https://api.myanimelist.net/v2/users/{username}/mangalist"

    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }
    
    params = {
        "fields": "list_status, genres",
        "sort": "list_updated_at",
        "limit": 50
    }

    try:
        response = requests.get(mal_api_url, headers=headers, params = params)
        response.raise_for_status()
        data = response.json()
        
        recent_activity = []

        seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
        
        for item in data.get("data", []):
            node = item.get("node", {})
            list_status = item.get("list_status", {})

            updated_str = list_status.get("updated_at")
            print(f"DEBUG: {node.get('title')} was last updated on {updated_str}")

            
            if updated_str:
                updated_at = datetime.fromisoformat(updated_str).timestamp()

                if updated_at >= seven_days_ago and list_status.get("status") in ["reading", "completed"]:
                    recent_activity.append({
                        "title" : node.get("title"),
                        "genres": [g.get("name") for g in node.get("genres", [])],
                        "status" : list_status.get("status")
                    })
            
        return recent_activity
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying MyAnimeList API: {e}")
        return []

# Fetches a user's entire MyAnimeList manga/anime collection
@lru_cache(maxsize=32)
def _fetch_myanimelist_user_list(username: str, media_type: str) -> list:
    mal_api_url = f"https://api.myanimelist.net/v2/users/{username}/{media_type.lower()}list"
    
    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }

    params = {
        "fields": "alternative_titles",
        "limit": 100
    }

    all_items = []
    
    while mal_api_url: 
        success = False
        for attempt in range(3):
            try:
                response = requests.get(mal_api_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
        
                all_items.extend(data.get("data", []))
                            
                paging = data.get("paging", {})
                next_url = paging.get("next")
                
                if next_url:
                    mal_api_url = next_url
                    params = {}
                else:
                    mal_api_url = None
                    
                success = True
                break
            except requests.exceptions.RequestException as e:
                status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else None
                print(f"DEBUG: MyAnimeList API Error {status_code}. Retrying ({attempt+1}/3)...")
                time.sleep(2)
                
        if not success:
            print("DEBUG: MyAnimeList API failed after 3 retries. Aborting list fetch.")
            break
            
    return all_items

# Checks if a title exists in the user's MyAnimeList.
def check_myanimelist_title_in_user_list(username: str, title: str, media_type: str) -> bool:
    print(f"DEBUG: Agent checking if '{title}' is in {username}'s list...")
    items = _fetch_myanimelist_user_list(username, media_type)
    search_title = title.lower()
    
    for item in items:
        node = item.get("node", {})
        
        all_titles = []
        if node.get("title"): all_titles.append(node.get("title"))
        
        alt = node.get("alternative_titles", {})
        if alt.get("en"): all_titles.append(alt.get("en"))
        if alt.get("ja"): all_titles.append(alt.get("ja"))
        if alt.get("synonyms"): all_titles.extend(alt.get("synonyms"))
        
        for t in all_titles:
            t_lower = t.lower()
            if difflib.SequenceMatcher(None, search_title, t_lower).ratio() > 0.7 or search_title in t_lower:
                return True
                
    return False

# Verifies if a title exists on MyAnimeList.
def verify_title_exists_on_mal(title: str, media_type: str) -> str:
    print(f"DEBUG: Agent verifying if '{title}' actually exists on MyAnimeList...")
    mal_api_url = f"https://api.myanimelist.net/v2/{media_type.lower()}"
    
    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }

    params = {
        "q": title,
        "limit": 1
    }

    try: 
        response = requests.get(mal_api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data"):
            node = data["data"][0].get("node", {})
            info = {
                "id": node.get("id"),
                "url": f"https://myanimelist.net/{media_type.lower()}/{node.get('id')}",
                "official_title": node.get("title")
            }
            return str(info)
            
        return "Not found"
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying MyAnimeList API: {e}")
        return "Not found"

    

