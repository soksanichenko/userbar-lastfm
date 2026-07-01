import os

SECRET_KEY = os.environ.get("SECRET_KEY")
LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
API_URL = os.environ.get("API_URL") or "http://ws.audioscrobbler.com/2.0"
PATH_TO_FONT = os.environ.get("PATH_TO_FONT") or "tahomabd.ttf"
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", False)
