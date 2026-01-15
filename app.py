import os
import json
import logging
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI 

from recommendations import generate_recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
NODE_API_URL = os.getenv("NODE_API_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, origins=["https://doomsday058.github.io"], supports_credentials=True)

openai_client = OpenAI(api_key=OPENAI_API_KEY)
http_session = requests.Session()

GENRE_MAP = {
    "боевик": "28", "экшн": "28", "приключения": "12", "драма": "18",
    "комедия": "35", "фэнтези": "14", "романтика": "10749", "триллер": "53",
    "ужасы": "27", "криминал": "80", "фантастика": "878", "мелодрама": "10749"
}

def get_gpt_response(messages, model="gpt-4o-mini", json_mode=False):
    """Обертка для вызова GPT с обработкой ошибок."""
    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": 0.7
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = openai_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return None

@app.route("/recommendations/<int:user_id>", methods=["GET"])
def get_recommendations_route(user_id):
    try:
        page = int(request.args.get("page", 1))
        page_size = 20
        
        all_recs = generate_recommendations(user_id)
        
        start = (page - 1) * page_size
        end = start + page_size
        return jsonify(all_recs[start:end])
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/generate_review/<int:tmdb_id>", methods=["GET"])
def generate_review(tmdb_id):
    content_type = request.args.get("type", "movie")
    if content_type not in ["movie", "serial"]:
        return jsonify({"error": "Invalid content type"}), 400

    endpoint = "movies" if content_type == "movie" else "series"
    
    try:
        resp = http_session.get(f"{NODE_API_URL}/api/{endpoint}/{tmdb_id}", timeout=5)
        if not resp.ok:
            return jsonify({"error": "Content not found"}), 404
        
        data = resp.json()
        
        title = data.get('title') or data.get('name')
        overview = data.get('overview', 'Описание отсутствует')
        genres = ', '.join([g['name'] for g in data.get('genres', [])])
        rating = data.get('vote_average', 0.0)

        tone = "критичен, укажи на недостатки" if rating < 7 else "позитивен, отметь сильные стороны"
        
        prompt = (
            f"Напиши обзор на фильм '{title}'. "
            f"Жанры: {genres}. Рейтинг: {rating}. Сюжет: {overview}. "
            f"Тон обзора: {tone}. "
            "Формат: Заголовок, затем текст без Markdown-выделений. Без спойлеров."
        )

        review_text = get_gpt_response(
            messages=[
                {"role": "system", "content": "Ты профессиональный кинокритик."},
                {"role": "user", "content": prompt}
            ]
        )

        return jsonify({"review": review_text if review_text else "Не удалось сгенерировать обзор."})

    except Exception as e:
        logger.error(f"Review generation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/advanced_search", methods=["GET"])
def advanced_search():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    system_prompt = (
        "Ты — API парсер. Извлеки из текста параметры поиска фильмов. "
        "Верни JSON с ключами: 'actors' (list), 'year_range' (list[min, max]), 'genres' (list). "
        "Если параметров нет, верни пустые списки."
    )
    
    gpt_json = get_gpt_response(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        model="gpt-3.5-turbo-0125", 
        json_mode=True
    )

    if not gpt_json:
        return jsonify({"error": "Failed to parse query"}), 500

    try:
        params = json.loads(gpt_json)
        logger.info(f"Parsed params: {params}")
        
        tmdb_params = {
            "api_key": TMDB_API_KEY,
            "language": "ru-RU",
            "sort_by": "popularity.desc",
            "page": 1
        }

        if len(params.get("year_range", [])) == 2:
            tmdb_params["primary_release_date.gte"] = f"{params['year_range'][0]}-01-01"
            tmdb_params["primary_release_date.lte"] = f"{params['year_range'][1]}-12-31"

        genre_ids = [GENRE_MAP[g.lower()] for g in params.get("genres", []) if g.lower() in GENRE_MAP]
        if genre_ids:
            tmdb_params["with_genres"] = ",".join(genre_ids)

        if params.get("actors"):
            actor_name = params["actors"][0]
            search_resp = http_session.get(
                "https://api.themoviedb.org/3/search/person",
                params={"api_key": TMDB_API_KEY, "query": actor_name},
                timeout=3
            )
            if search_resp.ok and search_resp.json()['results']:
                tmdb_params["with_cast"] = search_resp.json()['results'][0]['id']

        discover_resp = http_session.get("https://api.themoviedb.org/3/discover/movie", params=tmdb_params)
        
        if not discover_resp.ok:
            return jsonify({"error": "TMDB API Error"}), 502

        movies = discover_resp.json().get("results", [])
        return jsonify({"tmdbIds": [m["id"] for m in movies]})

    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return jsonify({"error": "Search processing failed"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)