import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from recs.consumers import RatingsConsumer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django_app = get_asgi_application()
application = ProtocolTypeRouter({"http": django_app, "websocket": URLRouter([ path("ws/ratings/", RatingsConsumer.as_asgi()) ])})
