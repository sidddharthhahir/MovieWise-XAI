# MovieWise XAI

A Django web app for personalized movie recommendations with explainable AI.

## Project Overview

MovieWise XAI combines hybrid recommendation modeling, TMDB-powered discovery, and natural-language explanations to help users understand why movies are recommended. It includes authentication, onboarding, rating flows, and a responsive UI for day-to-day use.

## Key Features

- Personalized recommendations using LightFM
- Explainable recommendations with local LLM + RAG
- TMDB-backed trending and discovery experiences
- Movie rating workflow that improves recommendations over time
- User onboarding and authentication
- Search and trailer access from the main UI

## Tech Stack

- **Backend:** Python 3.10, Django, Django REST Framework
- **ML/AI:** LightFM, scikit-learn, local LLM via Ollama
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
4. Configure environment variables in `.env` (for example `TMDB_API_KEY`, `OLLAMA_URL`, `OLLAMA_MODEL`).
5. Apply migrations and run the app:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Usage

- Open `http://localhost:8000`
- Sign up or log in
- Complete onboarding by rating movies
- Explore recommendations, trending content, search, and explanations

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

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request.

## License & Contact

Add your preferred license details in this repository and open an issue for support or collaboration questions.
