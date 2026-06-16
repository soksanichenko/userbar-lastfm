# lastfm-userbar — Claude Context

Flask app that generates Last.fm userbar PNG images. No database. Stateless per-request image generation via Pillow.

## Project structure

```
lastfm-userbar/
├── config.py                  # Env-var config (no Pydantic — plain os.environ)
├── wsgi.py                    # App factory, ProxyFix, force-HTTPS wrapper
├── pyproject.toml             # Project metadata and ruff config
├── requirements.txt           # Pinned deps
├── Dockerfile                 # python:3.12-slim, gunicorn on port 8100
├── main/
│   ├── __init__.py            # Blueprint definition (lastfm_app)
│   └── views.py               # All route handlers
├── utils/
│   ├── api.py                 # LastFmApi, User — Last.fm API client
│   ├── main.py                # Image rendering (gradient, text, logo)
│   ├── nocache.py             # @nocache decorator
│   └── utils.py               # parse_color_string, hex_to_rgb_tuple
├── static/
│   ├── tahomabd.ttf           # Default font
│   ├── arial.ttf
│   └── logo.png               # Last.fm logo for overlay
├── templates/
│   ├── index.html
│   ├── main.html              # Landing page
│   └── format1.html           # Generator UI
└── ansible/
    ├── ansible.cfg
    ├── requirements.yml
    ├── inventories/
    │   ├── zelgray.cherkasy.ua/   # Production inventory 1
    │   └── zelgray.work/          # Production inventory 2
    ├── playbooks/
    │   ├── deploy.yml
    │   └── pre_tasks/
    │       └── infisical.yml      # Loads secrets from Infisical
    └── roles/
        └── lastfm-userbar/
            ├── defaults/main.yml
            ├── handlers/main.yml
            ├── tasks/main.yml
            └── templates/
                ├── upstream.conf.j2
                └── location.conf.j2
```

## URL routes

| Route | Handler | Notes |
|---|---|---|
| `GET /` | `main` | Landing page; no-cache |
| `GET /generator`, `/format1.html` | `generator` | Generator UI |
| `GET /format2.html` | `format2_redirect` | Redirects to `/generator` |
| `GET /api/validate` | `api_validate` | `?username=` → JSON `{valid, error}` |
| `GET /<user>/userbar.png` | `new_user_bar` | Default colours |
| `GET /<user>/<params>/userbar.png` | `new_user_bar` | URL-encoded params, underscore-RGB |
| `GET /<user>/userbar2.png` | `new_user_bar2` | Abbreviated params, hex colours |
| `GET /<user>/<params>/userbar2.png` | `new_user_bar2` | Abbreviated params, hex colours |
| `GET /<user>/<ic>/<oc>/<tc>/userbar.png` | `user_bar` | Legacy: colours as path segments |

All image routes are decorated with `@nocache`.

## Configuration

Set via environment variables only (`config.py` uses `os.environ`):

| Variable | Default | Required |
|---|---|---|
| `SECRET_KEY` | `None` | Yes |
| `LASTFM_API_KEY` | `None` | Yes |
| `API_URL` | `http://ws.audioscrobbler.com/2.0` | No |
| `PATH_TO_FONT` | `tahomabd.ttf` | No |
| `FLASK_DEBUG` | `False` | No |

`PATH_TO_FONT` is a filename resolved relative to `lastfm_app.static_folder` at render time.

## Image rendering pipeline

`create_userbar` (utils/main.py):
1. Calls `user_get_last_track` → Last.fm API (`User.GetRecentTracks`)
2. Formats text: `{artist_name} - {track_name}` (or error string on failure)
3. `paste_text` → `gradient` → gradient PNG with text overlaid
4. `paste_logo` → composites `logo.png` onto right edge (only if `logo_color` is set)

Default image dimensions: 23 px tall, width grows with text (min 305 px, max 750 px with `truncate_text`).

## Key dependencies

| Package | Pinned version | Purpose |
|---|---|---|
| Flask | 3.1.3 | Web framework |
| Pillow | 12.2.0 | Image generation |
| requests | 2.34.2 | Last.fm API HTTP calls |
| gunicorn | 26.0.0 | WSGI server |

Python ≥ 3.10 required; Docker image uses 3.12-slim.

## Deployment

- Container exposes port 8100; Gunicorn runs with 2 workers.
- Ansible role `lastfm-userbar` syncs code via rsync, builds image, runs container, and updates nginx configs.
- Secrets (`SECRET_KEY`, `LASTFM_API_KEY`) are injected at deploy time from Infisical (keys: `lastfm-shared-secret-lastfm-userbar`, `lastfm-api-key-lastfm-userbar`).
- CI triggers on push to `master` via `.github/workflows/deploy.yml`.
- `wsgi.py` wraps the WSGI app with `_force_https` when `FLASK_DEBUG` is not set.

## Ansible collections

- `infisical.vault` (custom fork from GitHub)
- `community.docker`
- `ansible.posix`
