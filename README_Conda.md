# XAI Movie Recommendations System - Conda Setup Guide

## Quick Start

### Method 1: Using the batch script
```bash
activate_conda.bat
python manage.py runserver
```

### Method 2: Manual setup
```bash
conda env create -f environment.yml
conda activate xai-recs-django
python manage.py migrate
python manage.py runserver
```

## Complete Setup Steps

### 1. Install Miniconda/Anaconda (if not already installed)
- Download from: https://conda.io/miniconda.html
- Add conda to PATH during installation

### 2. Environment Setup:
```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Or create manually:
conda create -n xai-recs-django python=3.10 # Using python 3.10 as per environment.yml
conda activate xai-recs-django

# Install all packages via conda (prioritizing conda-forge)
conda env update -f environment.yml --prune
```

## Environment Management

### Update Environment:
```bash
# After modifying environment.yml
conda env update -f environment.yml --prune
```

### Environment Configuration Files:

1. **`environment.yml`** - Primary Conda environment specification
2. **`activate_conda.bat`** - Windows activation script
3. **`requirements_conda.txt`** - Alternative pip requirements (not used in this setup)
4. **`conda_setup.md`** - Detailed documentation (this file)

## Development Workflow

### Starting Development:
```bash
conda activate xai-recs-django
python manage.py runserver
# Access at: http://localhost:8000
```

### Key Management Commands:
```bash
# Migrate database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Data ingestion from TMDB
python manage.py tmdb_ingest --pages=3

# Train recommendation model
python manage.py train_lightfm
```

## Project Structure

```
xai_recs_full_v3_2_auth_ui/
├── environment.yml          # Conda environment specification
├── activate_conda.bat        # Windows activation script
├── conda_setup.md             # Detailed setup instructions (this file)
├── requirements_conda.txt      # Pip-compatible requirements (not used in this setup)
├── manage.py                   # Django management script
├── project/                    # Project settings
├── core/                       # Data models
├── recs/                       # Recommendation system
├── rag/                        # RAG search functionality
├── accounts/                   # User authentication
├── ui/                         # User interface
└── static/ & templates/         # Frontend assets
```

## Benefits of Conda Setup

### ✅ Advantages:
1. **Better Windows Support**: Pre-compiled binaries optimized for Windows
2. **Dependency Resolution**: Handles complex package dependencies better than pip
3. **Conda-Forge Stability**: Packages are thoroughly tested
4. **Simplified Installation**: All dependencies managed through `environment.yml`.
5. **Environment Isolation**: Separate from system Python packages
6. **Production Consistency**: Same environment across development and production

## Troubleshooting

### Common Issues:

1. **Conda not found**: Ensure Miniconda/Anaconda is installed and in PATH
2. **Package Conflicts**: Use `conda clean --all` and recreate environment if needed

### Verification:
```bash
# Test critical imports
python -c "import django; print('Django OK')"
python -c "import lightfm; print('LightFM OK')"
```

## Migration from Virtualenv

### If currently using .venv:
1. Deactivate current virtual environment
2. Recreate environment using `conda env create -f environment.yml`
3. Verify: `conda list | findstr django`
```

This Conda environment setup provides a robust foundation for your XAI recommendations system with better dependency management on Windows.