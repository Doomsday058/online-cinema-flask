<div align="center">

# AI-сервис "FilmAdviser" (Python/Flask)

_Вспомогательный бэкенд-сервис для генерации AI-рекомендаций и обзоров._

</div>

<p align="center">
    <img src="https://img.shields.io/badge/status-live-success?style=for-the-badge" alt="Статус">
    <img src="https://img.shields.io/github/last-commit/Doomsday058/online-cinema-flask?style=for-the-badge" alt="Последний коммит">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python">
</p>

---

### 🔗 **https://cinema-ai-service.onrender.com**

---

### 🏛️ Архитектура проекта

Этот сервис является частью full-stack системы. Он получает данные от основного Node.js API и отдает результаты на Frontend.

| Сервис | Описание | Репозиторий |
| :--- | :--- | :--- |
| 🎨 **Frontend (React)** | Пользовательский интерфейс. | **[Перейти](https://github.com/Doomsday058/online-cinema-frontend)** |
| ⚙️ **Backend (Node.js)** | Основной API для работы с пользователями. | **[Перейти](https://github.com/Doomsday058/online-cinema-backend)** |
| 🧠 **AI-Backend (Python)** | Сервис для генерации рекомендаций. | _(текущий)_ |

---

### 🚀 Основные возможности

| Функция | Описание |
| :--- | :--- |
| **🤖 Персональные рекомендации** | Анализирует избранное пользователя (жанры, актеры) и формирует ленту рекомендаций. |
| **✍️ Генерация обзоров с помощью AI** | Использует модель GPT для написания текстовых обзоров, адаптируя тон под рейтинг фильма. |
| **🔍 Расширенный поиск** | Обрабатывает запросы на естественном языке, преобразуя их в параметры для поиска по API. |

---

### 🛠️ Технологический стек

<p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
    <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn" />
    <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI API" />
    <img src="https://img.shields.io/badge/REST_API-000000?style=for-the-badge" alt="REST API" />
</p>

---

<details>
<summary>▶️ 📦  <strong>Инструкции по установке и запуску</strong></summary>

<br>

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
    source ven/bin/activate
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

</details>
