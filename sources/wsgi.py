from __future__ import annotations

import os

import config
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Configured Flask application instance.
    """
    from src.main import lastfm_app

    app = Flask(__name__, static_folder=os.path.join("src", "static"))
    app.config.from_object(config)
    app.register_blueprint(lastfm_app, url_prefix="/")
    app.url_map.strict_slashes = False
    app.wsgi_app = ProxyFix(app.wsgi_app)  # type: ignore[method-assign]
    return app


def _force_https(wsgi_app):
    def wrapper(environ, start_response):
        environ["wsgi.url_scheme"] = "https"
        return wsgi_app(environ, start_response)

    return wrapper


application = create_app()

if not os.environ.get("FLASK_DEBUG"):
    application.wsgi_app = _force_https(application.wsgi_app)  # type: ignore[method-assign]

if __name__ == "__main__":
    if os.environ.get("FLASK_DEBUG"):
        application.run(debug=True, host="0.0.0.0", port=8080)
