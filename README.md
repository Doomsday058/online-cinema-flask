<div align="center">

# 🎬 FilmAdviser AI Microservice

**Интеллектуальный движок рекомендаций и семантического поиска для онлайн-кинотеатра.**
<br>
*Часть экосистемы [Cinema Platform](https://github.com/Doomsday058/online-cinema-frontend)*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Flask-Lightweight-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/OpenAI-GPT--4-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Status-Production-success?style=for-the-badge" alt="Status" />
</p>

[🌐 Live Demo](https://cinema-ai-service.onrender.com) • [🐛 Report Bug](https://github.com/Doomsday058/online-cinema-flask/issues)

</div>

---

## 🏛️ О проекте

**FilmAdviser** — это изолированный микросервис на Python, отвечающий за ML-функции и сложную логику обработки данных в кинотеатре. В отличие от основного CRUD-бэкенда, этот сервис сфокусирован на **персонализации** и **NLP-обработке** запросов.

### Ключевые возможности:
* **🤖 Гибридная система рекомендаций:** Анализирует историю просмотров, выделяет веса (жанры, актеры, режиссеры) и ранжирует контент на основе скоринговой модели.
* **🧠 NLP-Search (Natural Language Processing):** Позволяет искать фильмы запросами вроде *"фильмы 90-х с Джимом Керри про криминал"*. Запрос парсится через GPT-3.5 в JSON-структуру фильтров.
* **✍️ AI-Reviewer:** Генерирует уникальные обзоры на фильмы с учетом их рейтинга и тональности, используя GPT-4o-mini.

---

## 🛠️ Архитектура и Технологии

Сервис выступает в роли интеллектуальной прослойки между Frontend и внешними API.

```mermaid
graph LR
    Client(Frontend React) -->|REST API| Flask(Flask Microservice)
    Flask -->|Fetch User History| Node(Node.js Backend)
    Flask -->|Semantic Parsing| OpenAI(OpenAI GPT API)
    Flask -->|Data Enrichment| TMDB(TMDB API)
    Flask -->|JSON Response| Client
