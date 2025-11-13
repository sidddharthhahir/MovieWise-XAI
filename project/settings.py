from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY=os.getenv("SECRET_KEY","dev")
DEBUG=bool(int(os.getenv("DEBUG","1")))
ALLOWED_HOSTS=[h.strip() for h in os.getenv("ALLOWED_HOSTS","").split(",") if h]
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','channels','accounts','core','recs','rag','ui']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='project.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='project.wsgi.application'; ASGI_APPLICATION='project.asgi.application'
DATABASES={'default': {'ENGINE':'django.db.backends.sqlite3','NAME': BASE_DIR/'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS=[]; LANGUAGE_CODE='en-us'; TIME_ZONE='Asia/Kolkata'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATICFILES_DIRS=[BASE_DIR/'static']; DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
REST_FRAMEWORK={'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.AllowAny']}
TMDB_API_KEY=os.getenv('TMDB_API_KEY',''); MODEL_DIR=str(BASE_DIR/'models'); os.makedirs(MODEL_DIR, exist_ok=True)
LOGIN_REDIRECT_URL='ui:app'
LOGOUT_REDIRECT_URL = '/'

LOGIN_URL = 'login'
