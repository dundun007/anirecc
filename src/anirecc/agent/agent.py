import os
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool
from anilist import (
    get_recent_anilist_anime as _get_recent_anilist_anime, 
    get_recent_anilist_manga as _get_recent_anilist_manga, 
    check_anilist_title_in_user_list as _check_anilist_title_in_user_list, 
    verify_title_exists_on_anilist as _verify_title_exists_on_anilist
)
from myanimelist import (
    get_recent_myanimelist_anime as _get_recent_myanimelist_anime, 
    get_recent_myanimelist_manga as _get_recent_myanimelist_manga,
    check_myanimelist_title_in_user_list as _check_myanimelist_title_in_user_list,
    verify_title_exists_on_mal as _verify_title_exists_on_mal
)

load_dotenv()

@tool
def get_recent_anilist_anime(username: str) -> str:
    """Get the recent anime activity for a given username."""
    return str(_get_recent_anilist_anime(username))

@tool
def get_recent_anilist_manga(username: str) -> str:
    """Get the recent manga activity for a given username."""
    return str(_get_recent_anilist_manga(username))

@tool
def check_anilist_title_in_user_list(username: str, title: str, media_type: str) -> bool:
    """Check if a title exists in the user's AniList."""
    return _check_anilist_title_in_user_list(username, title, media_type)

@tool
def verify_title_exists_on_anilist(title: str, media_type: str) -> str:
    """Check if a title actually exists in the global AniList database."""
    return _verify_title_exists_on_anilist(title, media_type)

@tool
def get_recent_myanimelist_anime(username: str) -> str:
    """Get the recent anime activity for a given username."""
    return str(_get_recent_myanimelist_anime(username))

@tool
def get_recent_myanimelist_manga(username: str) -> str:
    """Get the recent manga activity for a given username."""
    return str(_get_recent_myanimelist_manga(username))

@tool
def check_myanimelist_title_in_user_list(username: str, title: str, media_type: str) -> bool:
    """Check if a title exists in the user's MyAnimeList."""
    return _check_myanimelist_title_in_user_list(username, title, media_type)

@tool
def verify_title_exists_on_mal(title: str, media_type: str) -> str:
    """Check if a title actually exists in the global MyAnimeList database."""
    return _verify_title_exists_on_mal(title, media_type)

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0.7,
)

agent = create_agent(
    model=model,
    tools=[
        get_recent_anilist_anime, get_recent_anilist_manga, 
        get_recent_myanimelist_anime, get_recent_myanimelist_manga, 
        check_anilist_title_in_user_list, verify_title_exists_on_anilist,
        check_myanimelist_title_in_user_list, verify_title_exists_on_mal
    ],
    system_prompt="""
    You are a helpful assistant. Use the tools to get the recent anime and manga activity for a given 
    username and return a similar title to the recent activity in the same medium (anime or manga).
    "IMPORTANT: Before providing a recommendation, you MUST first use the appropriate check tool 
    (e.g., 'check_anilist_title_in_user_list' or 'check_myanimelist_title_in_user_list') to verify the user hasn't already read/watched it. 
    If they haven't, you MUST then use the corresponding verification tool (e.g., 'verify_title_exists_on_anilist' or 'verify_title_exists_on_mal') to get the database URL. 
    If either tool fails or returns 'Not found', try another title. 
    
    When you give your final recommendation, you MUST strictly use this exact format for the link at the very end of your response:
    You can view it on [Platform Name] here: [Official Title](URL)
    """)

if __name__ == "__main__":
    target_user = os.environ["TARGET_USER"]
    target_platform = os.environ["TARGET_PLATFORM"]
    target_media = os.environ["TARGET_MEDIA"]
    
    prompt = f"What is the recent {target_media} activity on {target_platform} for user {target_user}, and what {target_media} should they read next based on it?"
    print(f"Sending request to LLM for {target_user} on {target_platform} ({target_media})...")
    
    result = agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })
    
    print("\nResponse:")
    content = result["messages"][-1].content
    if isinstance(content, list):
        text_response = "".join(block.get("text", "") for block in content if isinstance(block, dict))
        print(text_response)
    else:
        print(content)