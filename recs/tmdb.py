# recs/tmdb.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w342"

def _session():
    s = requests.Session()
    retries = Retry(
        total=5,                # up to 5 attempts
        backoff_factor=0.8,     # 0.8, 1.6, 2.4, …
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

_session = _session()

def api(path, **params):
    params['api_key'] = settings.TMDB_API_KEY
    url = f"{BASE_URL}{path}"
    # 60s timeout (connect, read)
    r = _session.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def get_genres():
    return api('/genre/movie/list', language='en-US').get('genres', [])

def search_person(name):
    return api('/search/person', query=name, include_adult=False).get('results', [])

def discover(**kwargs):
    params = {'sort_by': 'popularity.desc', 'include_adult': False, 'language': 'en-US', 'page': 1}
    params.update(kwargs)
    return api('/discover/movie', **params).get('results', [])

def get_tmdb_trending(time_window='week', **kwargs):
    """Fetches trending movies directly from TMDB's /trending endpoint."""
    params = {'language': 'en-US'}
    params.update(kwargs)
    return api(f'/trending/movie/{time_window}', **params).get('results', [])

def detail(mid):
    return api(f'/movie/{mid}', append_to_response='credits')
