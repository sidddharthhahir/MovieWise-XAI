# MovieWise XAI

[![checks](https://github.com/sidddharthhahir/MovieWise-XAI/actions/workflows/checks.yml/badge.svg)](https://github.com/sidddharthhahir/MovieWise-XAI/actions/workflows/checks.yml)

A Django application for movie discovery, personalized recommendations, and explainable recommendation output.

## Project Overview

MovieWise XAI combines TMDB ingestion, recommendation ranking, and explanation endpoints in a single web app. Users can sign up, rate movies, complete onboarding, and request both score-based and natural-language recommendation explanations.

## Key Features

- Personalized recommendations with a LightFM-first pipeline and a content-based fallback
- Explainability endpoints with SHAP-like and LIME-like feature signals
- RAG-style context retrieval over local movie metadata
- TMDB-backed discovery and trending endpoints
- User authentication, onboarding flow, and rating capture

## Tech Stack

- **Backend:** Python 3.10, Django, Django REST Framework
- **ML/AI:** LightFM (optional), scikit-learn, local LLM via Ollama
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Data/API:** TMDB API
- **Database:** SQLite (default development setup)

## Setup & Run

1. Clone and enter the repository:
   ```bash
   git clone <repository_url> MovieWise-XAI
   cd MovieWise-XAI
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv_310
   source .venv_310/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env` (see `.env.example`).
5. Apply migrations and run the app:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Usage

- Open `http://localhost:8000`
- Sign up or log in
- Complete onboarding by rating movies
- Explore recommendations, trending content, and explanations

## Optional Data + Model Commands

```bash
python manage.py tmdb_ingest --pages=3
python manage.py train_lightfm --epochs=8
```

LightFM training is optional. If LightFM is unavailable, the app falls back to a content/popularity-based recommender.

## Project Structure

```text
MovieWise-XAI/
├── accounts/      # Authentication and account flows
├── core/          # Core models and shared services
├── project/       # Django settings and URL configuration
├── rag/           # Retrieval and explanation logic
├── recs/          # Recommendation and rating APIs
├── static/        # Frontend assets
├── templates/     # HTML templates
├── ui/            # UI views and routes
└── manage.py
```

## Development Notes

- No automated test suite is currently included in the repository.
- Use `python manage.py check` after configuration changes to validate Django settings.
