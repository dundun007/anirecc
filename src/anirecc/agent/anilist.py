import requests
import time

ANILIST_API_URL = "https://graphql.anilist.co"

# Fetches a user's AniList anime activity from the past 7 days.
def get_recent_anilist_activity(username: str) -> list[dict]:
    graphql_query = """
    query ($userName: String) {
      MediaListCollection(userName: $userName, type: ANIME, sort: UPDATED_TIME_DESC) {
        lists {
          name
          entries {
            media {
              title { 
                romaji 
                english 
              }
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
        "userName": username
    }
    
    try:
        response = requests.post(ANILIST_API_URL, json={'query': graphql_query, 'variables': variables})
        response.raise_for_status()
        data = response.json()
        
        lists = data.get("data", {}).get("MediaListCollection", {}).get("lists", [])
        
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying AniList API: {e}")
        return []

# Fetches a user's AniList manga activity from the past 7 days.
def get_recent_anilist_manga(username: str) -> list[dict]:
    graphql_query = """
    query ($userName: String) {
      MediaListCollection(userName: $userName, type: MANGA, sort: UPDATED_TIME_DESC) {
        lists {
          name
          entries {
            media {
              title { 
                romaji 
                english 
              }
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
        "userName": username
    }
    
    try:
        response = requests.post(ANILIST_API_URL, json={'query': graphql_query, 'variables': variables})
        response.raise_for_status()
        data = response.json()
        
        lists = data.get("data", {}).get("MediaListCollection", {}).get("lists", [])
        
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying AniList API: {e}")
        return []

'''
if __name__ == "__main__":
    import json
    results = get_recent_anilist_manga("saltaky")
    print(f"Found {len(results)} recent activities!")
    print(json.dumps(results, indent=2))
'''