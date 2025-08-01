# AI-сервис "FilmAdviser" (Python/Flask)

Это вспомогательный бэкенд-сервис, написанный на **Python и Flask**. Его главная задача — реализация интеллектуальных функций: генерация персональных рекомендаций и создание обзоров на фильмы с помощью **OpenAI API**.

### 🔗 **https://zass.ro/other-pages/centre-service.html(https://cinema-ai-service.onrender.com)**

---

### 🚀 Основные возможности

* **Персональные рекомендации:** Анализирует "избранное" пользователя (жанры, актеры, режиссеры) и формирует уникальную ленту рекомендаций.
* **Генерация обзоров с помощью AI:** Использует модель **GPT** для написания текстовых обзоров на фильмы и сериалы, адаптируя тон (критичный/положительный) в зависимости от рейтинга.
* **Расширенный поиск:** Обрабатывает запросы на естественном языке, преобразуя их в параметры для поиска по API.

---

### 🛠️ Технологический стек

* **Python**
* **Flask** (веб-фреймворк)
* **Gunicorn** (production-сервер)
* **OpenAI API**
* **Requests**

---

### 📦 Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone [https://github.com/Doomsday058/online-cinema-flask.git](https://github.com/Doomsday058/online-cinema-flask.git)
    cd online-cinema-flask
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Создайте файл `.env`** в корне проекта и добавьте переменные:
    ```
    # API ключ для OpenAI
    OPENAI_API_KEY="sk-..."

    # API ключ для The Movie Database
    TMDB_API_KEY="..."

    # URL развернутого Node.js сервера
    NODE_API_URL="https://..."
    ```

5.  **Запустите сервер:**
    ```bash
    flask run
    ```
