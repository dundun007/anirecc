import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
MAL_CLIENT_ID = os.getenv("MAL_CLIENT_ID")

# Fetches a user's MyAnimeList anime activity from the past 7 days.
def get_recent_myanimelist_anime(username: str) -> list[dict]:
    malApiUrl = f"https://api.myanimelist.net/v2/users/{username}/animelist"

    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }
    
    params = {
        "fields": "list_status, genres",
        "sort": "list_updated_at",
        "limit": 50
    }

    try:
        response = requests.get(malApiUrl, headers=headers, params = params)
        response.raise_for_status()
        data = response.json()
        
        recentActivity = []

        sevenDaysAgo = int(time.time()) - (7 * 24 * 60 * 60)
        
        for item in data.get("data", []):
            node = item.get("node", {})
            listStatus = item.get("list_status", {})

            updatedStr = listStatus.get("updated_at")
            
            if updatedStr:
                updatedAt = datetime.fromisoformat(updatedStr).timestamp()

                if updatedAt >= sevenDaysAgo and listStatus.get("status") in ["watching", "completed"]:
                    recentActivity.append({
                        "title" : node.get("title"),
                        "genres": [g.get("name") for g in node.get("genres", [])],
                        "status" : listStatus.get("status")
                    })
            
        return recentActivity
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying MyAnimeList API: {e}")
        return []

# Fetches a user's MyAnimeList manga activity from the past 7 days.
def get_recent_myanimelist_manga(username: str) -> list[dict]:
    malApiUrl = f"https://api.myanimelist.net/v2/users/{username}/mangalist"

    headers = {
        "X-MAL-CLIENT-ID": MAL_CLIENT_ID
    }
    
    params = {
        "fields": "list_status, genres",
        "sort": "list_updated_at",
        "limit": 50
    }

    try:
        response = requests.get(malApiUrl, headers=headers, params = params)
        response.raise_for_status()
        data = response.json()
        
        recentActivity = []

        sevenDaysAgo = int(time.time()) - (7 * 24 * 60 * 60)
        
        for item in data.get("data", []):
            node = item.get("node", {})
            listStatus = item.get("list_status", {})

            updatedStr = listStatus.get("updated_at")
            print(f"DEBUG: {node.get('title')} was last updated on {updatedStr}")

            
            if updatedStr:
                updatedAt = datetime.fromisoformat(updatedStr).timestamp()

                if updatedAt >= sevenDaysAgo and listStatus.get("status") in ["reading", "completed"]:
                    recentActivity.append({
                        "title" : node.get("title"),
                        "genres": [g.get("name") for g in node.get("genres", [])],
                        "status" : listStatus.get("status")
                    })
            
        return recentActivity
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying MyAnimeList API: {e}")
        return []
    
'''
if __name__ == "__main__":
    import json
    results = get_recent_myanimelist_manga("dundun007")
    print(f"Found {len(results)} recent activities!")
    print(json.dumps(results, indent=2))
'''

    

