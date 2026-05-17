from __future__ import annotations

import logging
from urllib.parse import parse_qsl

from flask import Response, jsonify, redirect, render_template, request, send_file, url_for

from config import LASTFM_API_KEY
from main import lastfm_app
from utils.api import LastFmException, User
from utils.main import create_userbar
from utils.nocache import nocache
from utils.utils import hex_to_rgb_tuple, parse_color_string

logger = logging.getLogger(__name__)

_COLOR_KEYS = frozenset({'inner_color', 'outer_color', 'text_color', 'border_color', 'logo_color'})

_ABBREV_MAP = {
    'ic': 'inner_color',
    'oc': 'outer_color',
    'tc': 'text_color',
    'bc': 'border_color',
    'lc': 'logo_color',
    'tt': 'truncate_text',
}

_DEFAULT_IMG_DATA: dict[str, object] = {
    'inner_color': (0, 0, 0),
    'outer_color': (255, 255, 255),
    'text_color': (255, 255, 255),
    'border_color': None,
    'logo_color': None,
    'truncate_text': False,
}


@lastfm_app.route('/api/validate')
def api_validate() -> Response:
    """Return JSON indicating whether a Last.fm username is valid."""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'valid': False, 'error': 'Username is required'})
    user = User(LASTFM_API_KEY, username=username)
    try:
        user.user_get_recent_tracks(extended=1)
        return jsonify({'valid': True})
    except LastFmException as exc:
        return jsonify({'valid': False, 'error': exc.message})


@lastfm_app.route('/format1.html')
@lastfm_app.route('/generator')
def generator() -> str:
    """Render the userbar generator page."""
    return render_template('format1.html',
                           title='Last.Fm UserBar Generator',
                           root_url=request.url_root)


@lastfm_app.route('/format2.html')
def format2_redirect() -> Response:
    """Redirect legacy /format2.html to the unified generator."""
    return redirect(url_for('lastfm_app.generator'))


@lastfm_app.route('/')
@nocache
def main() -> str:
    """Render the main landing page."""
    return render_template('main.html', title='Last.Fm UserBar', root_url=request.url_root)


@lastfm_app.route('/<username>/<inner_color>/<outer_color>/<text_color>/userbar.png')
@nocache
def user_bar(username: str, inner_color: str, outer_color: str, text_color: str) -> Response:
    """Legacy route: colours as separate path segments (underscore-RGB format)."""
    img = create_userbar(
        username,
        inner_color=parse_color_string(inner_color),
        outer_color=parse_color_string(outer_color),
        text_color=parse_color_string(text_color),
    )
    img.seek(0)
    return send_file(img, mimetype='image/png')


@lastfm_app.route('/<username>/userbar.png')
@lastfm_app.route('/<username>/<params>/userbar.png')
@nocache
def new_user_bar(username: str, params: str | None = None) -> Response:
    """Render a userbar PNG; colours passed as underscore-RGB query params in the path."""
    img_data = dict(_DEFAULT_IMG_DATA)
    if params:
        for key, value in parse_qsl(params):
            if key in _COLOR_KEYS:
                img_data[key] = parse_color_string(value) if value != 'None' else None
            elif key == 'truncate_text':
                img_data['truncate_text'] = value == 'True'
    img = create_userbar(username, **img_data)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@lastfm_app.route('/<username>/userbar2.png')
@lastfm_app.route('/<username>/<params>/userbar2.png')
@nocache
def new_user_bar2(username: str, params: str | None = None) -> Response:
    """Legacy v2 route: abbreviated param names and hex colour values."""
    img_data = dict(_DEFAULT_IMG_DATA)
    if params:
        for abbrev, value in parse_qsl(params):
            verbose = _ABBREV_MAP.get(abbrev)
            if verbose is None:
                continue
            if verbose in _COLOR_KEYS:
                img_data[verbose] = hex_to_rgb_tuple(value) if value != 'None' else None
            elif verbose == 'truncate_text':
                img_data['truncate_text'] = value == 'True'
    img = create_userbar(username, **img_data)
    img.seek(0)
    return send_file(img, mimetype='image/png')
