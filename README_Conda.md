# MovieWise XAI (Conda Setup)

A Conda-first setup guide for running MovieWise XAI consistently across environments.

## Project Overview

This guide provides a clean Conda workflow for creating, activating, and maintaining the MovieWise XAI environment, then running the Django application with the expected dependencies.

## Key Features

- Reproducible environment from `environment.yml`
- Straightforward setup for local development
- Standard Django management workflow support
- Helpful verification and troubleshooting steps

## Tech Stack

- **Runtime:** Python 3.10 (Conda-managed)
- **Framework:** Django + Django REST Framework
- **ML/AI:** LightFM and supporting data libraries
- **Environment Management:** Conda / conda-forge

## Setup & Run

1. Create the Conda environment:
   ```bash
   conda env create -f environment.yml
   ```
2. Activate the environment:
   ```bash
   conda activate xai-recs-django
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```

## Usage

- Open `http://localhost:8000`
- Use normal app flows (auth, onboarding, ratings, recommendations)
- Retrain and ingest data as needed:
  ```bash
  python manage.py tmdb_ingest --pages=3
  python manage.py train_lightfm
  ```

## Project Structure

```text
MovieWise-XAI/
├── environment.yml
├── requirements_conda.txt
├── conda_setup.md
├── manage.py
├── project/
├── core/
├── recs/
├── rag/
├── accounts/
├── ui/
└── static/ + templates/
```

## Contributing

Please keep setup instructions aligned with `environment.yml` and open a pull request for documentation improvements.

## Notes

- LightFM availability can vary by platform; fallback recommendation logic remains available.
