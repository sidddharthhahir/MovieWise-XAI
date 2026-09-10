# Conda setup

## Create environment

```bash
conda env create -f environment.yml
conda activate xai-recs-django
```

## Run application

```bash
python manage.py migrate
python manage.py runserver
```

## Update environment after dependency changes

```bash
conda env update -f environment.yml
```

## Verify core packages

```bash
python -c "import django, rest_framework, channels, sklearn"
```
