# recommendations.py

import os
from dotenv import load_dotenv
import requests
from collections import Counter
from functools import lru_cache

# Загружаем переменные окружения из файла .env
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
NODE_API_URL = os.getenv("NODE_API_URL")

def get_user_favorites(user_id):
    """Получаем избранные фильмы и сериалы пользователя через API."""
    url = f"{NODE_API_URL}/api/favorites/{user_id}"
    response = requests.get(url)
    favorites = response.json()
    # Преобразуем данные в нужный формат
    return [{"tmdbId": fav['tmdbId'], "type": fav['type']} for fav in favorites]

@lru_cache(maxsize=None)
def fetch_details_and_credits(tmdb_id, content_type):
    """Получаем детали и кредиты (актеры и режиссеры) с TMDb."""
    if content_type == 'movie':
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    else:
        url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"

    params = {
        "api_key": API_KEY,
        "language": "ru-RU",
        "append_to_response": "credits"
    }
    response = requests.get(url, params=params)
    return response.json()

def generate_recommendations(user_id):
    """Основной алгоритм генерации рекомендаций."""
    favorites = get_user_favorites(user_id)
    genre_weights = Counter()
    actor_weights = Counter()
    director_weights = Counter()

    # 1. Анализ избранного
    for favorite in favorites:
        data = fetch_details_and_credits(favorite["tmdbId"], favorite["type"])

        # Увеличиваем веса жанров
        genres = data.get("genres", [])
        for genre in genres:
            genre_weights[genre["id"]] += 5  # Увеличиваем вес жанра

        # Увеличиваем веса актеров
        credits = data.get("credits", {})
        for actor in credits.get("cast", [])[:5]:  # Только топ-5 актеров
            actor_weights[actor["id"]] += 3

        # Увеличиваем веса режиссеров
        for crew_member in credits.get("crew", []):
            if crew_member["job"] == "Director":
                director_weights[crew_member["id"]] += 2

    # 2. Поиск рекомендаций
    recommended_items = []

    # Получаем рекомендации для фильмов
    movie_recommendations = fetch_recommendations('movie')
    recommended_items.extend(movie_recommendations)

    # Получаем рекомендации для сериалов
    tv_recommendations = fetch_recommendations('tv')
    recommended_items.extend(tv_recommendations)

    # Исключаем избранное
    favorite_ids = set((fav["tmdbId"], fav["type"]) for fav in favorites)
    recommended_items = [
        item for item in recommended_items
        if (item["id"], 'movie' if item["media_type"] == 'movie' else 'serial') not in favorite_ids
    ]

    # Фильтруем уникальные элементы
    unique_recommendations = {}
    for item in recommended_items:
        key = (item["id"], item["media_type"])
        if key not in unique_recommendations:
            unique_recommendations[key] = item

    # Преобразуем обратно в список
    recommended_items = list(unique_recommendations.values())

    # 3. Ранжирование
    recommendations = []
    for item in recommended_items:
        score = 0
        data = fetch_details_and_credits(item["id"], item["media_type"])

        # Учитываем жанры
        genres = data.get("genres", [])
        for genre in genres:
            score += genre_weights[genre["id"]]

        # Учитываем актеров
        credits = data.get("credits", {})
        for actor in credits.get("cast", [])[:5]:
            score += actor_weights[actor["id"]]

        # Учитываем режиссеров
        for crew_member in credits.get("crew", []):
            if crew_member["job"] == "Director":
                score += director_weights[crew_member["id"]]

        recommendations.append({**item, "score": score})

    # Сортируем по оценке
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    # Получаем первые несколько десятков фильмов и сериалов с наивысшим баллом
    top_recommendations = recommendations[:20]

    # Добавляем оставшиеся из популярных фильмов и сериалов
    remaining_items = [item for item in recommended_items if item not in top_recommendations]
    remaining_items.sort(key=lambda x: x.get('popularity', 0), reverse=True)

    # Объединяем списки
    final_recommendations = top_recommendations + remaining_items[:20]  # Итоговый список из 50 рекомендаций

    return final_recommendations

def fetch_recommendations(content_type, total_pages=5):
    """Получаем рекомендации через API Discover с несколькими страницами."""
    if content_type == 'movie':
        url = "https://api.themoviedb.org/3/discover/movie"
        media_type = 'movie'
    else:
        url = "https://api.themoviedb.org/3/discover/tv"
        media_type = 'tv'

    all_results = []
    for page in range(1, total_pages + 1):
        response = requests.get(url, params={
            "api_key": API_KEY,
            "language": "ru-RU",
            "sort_by": "popularity.desc",
            "vote_average.gte": 5,
            "vote_count.gte": 100,
            "with_original_language": "en",
            "page": page
        })
        if response.ok:
            results = response.json().get("results", [])
            for item in results:
                item["media_type"] = media_type
            all_results.extend(results)

    # Убираем дубли на уровне fetch_recommendations
    unique_items = {f"{item['id']}_{item['media_type']}": item for item in all_results}
    return list(unique_items.values())

if __name__ == "__main__":
    user_id = 1  # Идентификатор пользователя
    recommendations = generate_recommendations(user_id)
    for rec in recommendations:
        title = rec.get('title') or rec.get('name')
        print(f"{title} (score: {rec['score']})")
