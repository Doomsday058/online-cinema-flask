import os
import logging
from typing import List, Dict, Any, Set
from collections import Counter
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
NODE_API_URL = os.getenv("NODE_API_URL")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
WEIGHTS = {
    "genre": 5,
    "actor": 3,
    "director": 2
}

session = requests.Session()

def get_headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {TMDB_API_KEY}"} if not TMDB_API_KEY else {}

def get_user_favorites(user_id: int) -> List[Dict[str, Any]]:
    """Fetch user favorites from the internal Node.js API."""
    try:
        response = session.get(f"{NODE_API_URL}/api/favorites/{user_id}", timeout=5)
        response.raise_for_status()
        data = response.json()
        return [{"tmdbId": item['tmdbId'], "type": item['type']} for item in data]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch favorites for user {user_id}: {e}")
        return []

@lru_cache(maxsize=128)
def fetch_tmdb_details(tmdb_id: int, content_type: str) -> Dict[str, Any]:
    """Fetch detailed info including credits. Cached to prevent redundant calls."""
    endpoint = "movie" if content_type == 'movie' else "tv"
    url = f"{TMDB_BASE_URL}/{endpoint}/{tmdb_id}"
    
    params = {
        "api_key": TMDB_API_KEY,
        "language": "ru-RU",
        "append_to_response": "credits"
    }
    
    try:
        response = session.get(url, params=params, timeout=3)
        return response.json() if response.ok else {}
    except requests.RequestException:
        return {}

def build_user_profile(favorites: List[Dict[str, Any]]) -> tuple[Counter, Counter, Counter]:
    """Analyze favorites to build preference vectors."""
    genres = Counter()
    actors = Counter()
    directors = Counter()

    for fav in favorites:
        data = fetch_tmdb_details(fav["tmdbId"], fav["type"])
        if not data:
            continue

        for genre in data.get("genres", []):
            genres[genre["id"]] += WEIGHTS["genre"]

        credits = data.get("credits", {})
        
        for actor in credits.get("cast", [])[:5]:
            actors[actor["id"]] += WEIGHTS["actor"]

        for crew in credits.get("crew", []):
            if crew["job"] == "Director":
                directors[crew["id"]] += WEIGHTS["director"]

    return genres, actors, directors

def fetch_candidates(content_type: str, pages: int = 3) -> List[Dict[str, Any]]:
    """Fetch popular items from TMDB to form a candidate pool."""
    endpoint = "movie" if content_type == 'movie' else "tv"
    url = f"{TMDB_BASE_URL}/discover/{endpoint}"
    
    candidates = []
    for page in range(1, pages + 1):
        params = {
            "api_key": TMDB_API_KEY,
            "language": "ru-RU",
            "sort_by": "popularity.desc",
            "vote_average.gte": 5,
            "vote_count.gte": 100,
            "page": page
        }
        try:
            resp = session.get(url, params=params, timeout=3)
            if resp.ok:
                results = resp.json().get("results", [])
                for item in results:
                    item["media_type"] = content_type
                candidates.extend(results)
        except requests.RequestException:
            continue
            
    return candidates

def calculate_score(item: Dict[str, Any], profile_genres: Counter) -> int:
    """
    Lightweight scoring based on data available in the list view (genres).
    Avoiding detailed fetch for every candidate to improve performance.
    """
    score = 0
    for genre_id in item.get("genre_ids", []):
        if genre_id in profile_genres:
            score += profile_genres[genre_id]
            
    score += int(item.get("popularity", 0) / 10)
    return score

def generate_recommendations(user_id: int) -> List[Dict[str, Any]]:
    favorites = get_user_favorites(user_id)
    if not favorites:
        return []

    profile_genres, profile_actors, profile_directors = build_user_profile(favorites)
    
    candidates = fetch_candidates('movie') + fetch_candidates('tv')
    
    fav_ids = {(f["tmdbId"], f["type"]) for f in favorites}
    candidates = [c for c in candidates if (c["id"], c["media_type"]) not in fav_ids]
    unique_candidates = {f"{c['id']}_{c['media_type']}": c for c in candidates}.values()


    scored_items = []
    for item in unique_candidates:
        item["score"] = calculate_score(item, profile_genres)
        scored_items.append(item)

    scored_items.sort(key=lambda x: x["score"], reverse=True)

    return scored_items[:20]

if __name__ == "__main__":
    recs = generate_recommendations(user_id=1)
    for i, r in enumerate(recs, 1):
        title = r.get('title') or r.get('name')
        print(f"{i}. {title} (Score: {r['score']})")