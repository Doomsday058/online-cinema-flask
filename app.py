# app.py
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from recommendations import generate_recommendations
import openai
import requests
import json

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
NODE_API_URL = os.getenv("NODE_API_URL")

app = Flask(__name__)

cors = CORS(app, resources={
    r"/generate_review/*": {
        "origins": "https://doomsday058.github.io"
    },
    r"/recommendations/*": {
        "origins": "https://doomsday058.github.io"
    },
    # Добавим сюда и advanced_search на всякий случай
    r"/advanced_search": {
        "origins": "https://doomsday058.github.io"
    }
})


@app.route("/recommendations/<int:user_id>", methods=["GET"])
def recommendations(user_id):
    try:
        page = int(request.args.get("page", 1))
        total_pages = 5
        recommendations = generate_recommendations(user_id)
        start_index = (page - 1) * 20
        end_index = start_index + 20
        paginated_recommendations = recommendations[start_index:end_index]
        return jsonify(paginated_recommendations)
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate_review/<int:tmdb_id>", methods=["GET"])
def generate_review(tmdb_id):
    try:
        content_type = request.args.get("type", "movie")
        if content_type not in ["movie", "serial"]:
            return jsonify({"error": "Invalid content type"}), 400

        if content_type == "movie":
            response = requests.get(f"{NODE_API_URL}/api/movies/{tmdb_id}")
        else:
            response = requests.get(f"{NODE_API_URL}/api/series/{tmdb_id}")

        if not response.ok:
            return jsonify({"error": "Failed to fetch content details"}), 500

        data = response.json()

        title = data.get('title') or data.get('name')
        overview = data.get('overview', '')
        genres = ', '.join([genre['name'] for genre in data.get('genres', [])])
        release_date = data.get('release_date') or data.get('first_air_date', '')
        runtime = data.get('runtime') or (data.get('episode_run_time')[0] if data.get('episode_run_time') else '')
        rating = data.get('vote_average', 0.0)

        if rating < 7:
            tone_instruction = (
                "Фильм получил не очень высокую оценку, поэтому будь более критичен. "
                "Укажи на недостатки, слабые стороны сюжета, игры актеров или визуальной части, но без спойлеров."
            )
        else:
            tone_instruction = (
                "Фильм оценен довольно высоко, поэтому дай больше положительных впечатлений, "
                "отметь сильные стороны, но без излишнего повторения уже известных фактов."
            )
        prompt = (
            f"Ты — профессиональный кинокритик. Тебе дан фильм {title}. "
            f"Жанры: {genres}, дата выхода: {release_date}, продолжительность: {runtime} минут. "
            f"Краткое описание: {overview}\n\n"
            "Твоя задача: Написать обзор фильма. В обзоре:\n"
            "- Начни с заголовка: 'Обзор фильма \"Название\"', заменив 'Название' на реальное название.\n"
            "- Не используй жирный шрифт или специальные выделения (**...**). Просто обычный текст.\n"
            "- Не повторяй снова дату выхода, жанры, продолжительность — они уже известны.\n"
            "- Обзор должен быть без спойлеров.\n"
            "- Если рейтинг низкий (меньше 7), будь более критичен и укажи на слабые стороны.\n"
            "- Если рейтинг 7 или выше, делай обзор более положительным, но не повторяй уже данные факты.\n"
            "- Не восхваляй технические детали, просто охарактеризуй впечатления, атмосферу, игру актеров, сюжетные качества.\n\n"
            f"Рейтинг фильма: {rating}. {tone_instruction}\n\n"
            "Напиши обзор."
        )

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — профессиональный критик фильмов и сериалов."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7,
        )

        review = completion.choices[0].message['content'].strip()

        return jsonify({"review": review})

    except Exception as e:
        print(f"Error generating review: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/advanced_search", methods=["GET"])
def advanced_search():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    try:
        prompt = (
            f"Обработай следующий запрос: \"{query}\".\n"
            "Выдели актеров, диапазон лет (year_range) и жанры.\n"
            "Верни результат строго в формате JSON, без лишнего текста, без пояснений.\n"
            "Пример:\n"
            "{\n"
            "  \"actors\": [\"Имя актёра\", \"Имя актёра 2\"],\n"
            "  \"year_range\": [1990, 2000],\n"
            "  \"genres\": [\"драма\", \"комедия\"]\n"
            "}\n\n"
            "Не добавляй лишнего текста, комментариев или кода. Только JSON."
        )

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — помощник, который возвращает только структурированные данные."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5,
        )

        processed_query = completion.choices[0].message['content'].strip()
        print("Processed query from GPT:", processed_query)

        start = processed_query.find('{')
        end = processed_query.rfind('}')
        if start == -1 or end == -1:
            return jsonify({"error": "Failed to find JSON braces"}), 500

        json_str = processed_query[start:end + 1]

        try:
            params = json.loads(json_str)
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse JSON from OpenAI"}), 500

        actors = params.get("actors", [])
        year_range = params.get("year_range", [])
        genres = params.get("genres", [])

        genre_map = {
            "боевик": "28", "экшн": "28", "приключения": "12", "драма": "18",
            "комедия": "35", "фэнтези": "14", "романтика": "10749", "триллер": "53",
            "ужасы": "27", "криминал": "80", "фантастика": "878", "мелодрама": "10749"
        }

        genre_ids = [genre_map[g.strip().lower()] for g in genres if g.strip().lower() in genre_map]

        cast_id = None
        if actors:
            person_resp = requests.get("https://api.themoviedb.org/3/search/person", params={
                "api_key": TMDB_API_KEY,
                "language": "ru-RU",
                "query": actors[0]
            })
            if person_resp.ok and person_resp.json().get("results"):
                cast_id = person_resp.json()["results"][0]["id"]

        search_params = {
            "language": "ru-RU", "sort_by": "popularity.desc", "include_adult": False,
            "include_video": False, "page": 1
        }

        if year_range and len(year_range) == 2:
            search_params["primary_release_date.gte"] = f"{year_range[0]}-01-01"
            search_params["primary_release_date.lte"] = f"{year_range[1]}-12-31"

        if genre_ids: search_params["with_genres"] = ",".join(genre_ids)
        if cast_id: search_params["with_cast"] = str(cast_id)

        print("Final TMDb search params:", search_params)

        response = requests.get(f"{NODE_API_URL}/api/discover/movie", params=search_params)

        if not response.ok:
            print("TMDb discover error:", response.text)
            return jsonify({"error": "Failed to fetch movies from TMDb"}), 500

        movies = response.json()
        tmdbIds = [m["id"] for m in movies]
        return jsonify({"tmdbIds": tmdbIds})

    except Exception as e:
        print(f"Error in advanced_search: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)