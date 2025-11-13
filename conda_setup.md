# Conda Environment Setup for XAI Recommendations System

## Quick Setup Commands

### 1. Create and activate Conda environment:
```bash
conda env create -f environment.yml
conda activate xai-recs-django
```

### 2. Environment Details:
```bash
# Check environment info
conda info
conda list

# Update environment (after modifying environment.yml)
conda env update -f environment.yml

### 2. Check installed packages:
```bash
conda list
```

## Conda Environment Structure

### Environment Configuration:
- **Name**: `xai-recs-django`
- **Python Version**: 3.9
- **Package Sources**: conda-forge, defaults
- **Key Packages**:
  - `django>=5.0, djangorestframework, channels, requests
  - ML Stack: `numpy`, `scikit-learn`, `joblib`
- **LightFM**: Installed via pip (not available in conda)
- **Windows Optimized**: Using conda-forge for better Windows compatibility

### Benefits of Conda Environment:

1. **Better Dependency Management**: Handles compiled packages better than pip
2. **Windows Optimization**: Pre-compiled binaries optimized for Windows
3. **Isolated Environment**: Prevents conflicts with system packages

## Using the Environment

### Development:
```bash
conda activate xai-recs-django
python manage.py runserver
```

### Managing Dependencies:
```bash
# Add new packages to environment.yml and update:
conda env update -f environment.yml

### Testing Environment:
```bash
# Verify Django installation
python -c "import django; print(django.VERSION)"
```

## Alternative Setup Methods

### Create from scratch:
```bash
conda create -n xai-recs-django python=3.9 django=5.0 djangorestframework channels requests python-dotenv numpy -c conda-forge
pip install scikit-learn joblib lightfm
```

### Environment Verification:
```bash
# Test key imports
python -c "import django, rest_framework, channels, sklearn, lightfm"
```

### Export Environment:
```bash
# Export current environment (optional)
conda env export > environment_frozen.yml
```

### Notes:
- The environment.yml file should be committed to version control
- For production deployment, use the same environment configuration
- LightFM is installed via pip since it's not available in conda repositories