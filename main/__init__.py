import os

from flask import Blueprint

lastfm_app = Blueprint(
    'lastfm_app',
    __name__,
    template_folder=os.path.join('..', 'templates'),
    static_folder=os.path.join('..', 'static'),
)

from . import views  # noqa: E402, F401
