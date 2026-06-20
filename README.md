# lastfm-userbar

Flask web app that generates userbar PNG images showing a Last.fm user's currently playing or most recently scrobbled track.

## Features

### Userbar generation

Generates a 23 px tall PNG banner with a horizontal colour gradient, the track text, and an optional Last.fm logo overlay.

**Routes:**

| Route | Description |
|---|---|
| `GET /` | Landing page |
| `GET /generator` or `/format1.html` | Interactive generator UI |
| `GET /api/validate?username=<name>` | JSON: checks whether a Last.fm username exists |
| `GET /<username>/userbar.png` | Userbar with default colours |
| `GET /<username>/<params>/userbar.png` | Userbar with URL-encoded params (underscore-RGB) |
| `GET /<username>/userbar2.png` | Userbar with default colours (v2 abbreviated params) |
| `GET /<username>/<params>/userbar2.png` | Userbar with abbreviated params and hex colours |
| `GET /<username>/<inner>/<outer>/<text>/userbar.png` | Legacy route: colours as separate path segments |

**Params for `userbar.png`** (URL-encoded query string in the path segment):

| Key | Format | Default | Description |
|---|---|---|---|
| `inner_color` | `R_G_B` | `0_0_0` | Left-side gradient colour |
| `outer_color` | `R_G_B` | `255_255_255` | Right-side gradient colour |
| `text_color` | `R_G_B` | `255_255_255` | Text colour |
| `border_color` | `R_G_B` or `None` | `None` | Optional 2 px border |
| `logo_color` | `R_G_B` or `None` | `None` | Optional logo overlay colour |
| `truncate_text` | `True` or `False` | `False` | Cap bar width at 750 px and truncate text at 95 chars |

**Abbreviated params for `userbar2.png`** (hex colour values):

| Key | Full name |
|---|---|
| `ic` | `inner_color` |
| `oc` | `outer_color` |
| `tc` | `text_color` |
| `bc` | `border_color` |
| `lc` | `logo_color` |
| `tt` | `truncate_text` |

## Requirements

- Python 3.10+
- A Last.fm API key

## Configuration

Set via environment variables:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | Flask secret key (required) |
| `LASTFM_API_KEY` | — | Last.fm API key (required) |
| `API_URL` | `http://ws.audioscrobbler.com/2.0` | Last.fm API base URL |
| `PATH_TO_FONT` | `tahomabd.ttf` | Font filename inside the `static/` directory |
| `FLASK_DEBUG` | `False` | Enable Flask debug mode |

## Running locally

```bash
pip install -r requirements.txt
SECRET_KEY=dev LASTFM_API_KEY=<your-key> python wsgi.py
```

Or with Gunicorn:

```bash
SECRET_KEY=dev LASTFM_API_KEY=<your-key> gunicorn --workers=2 --bind=0.0.0.0:8080 wsgi:application
```

Or with Docker:

```bash
docker build -t lastfm-userbar .
docker run -p 8100:8100 \
  -e SECRET_KEY=dev \
  -e LASTFM_API_KEY=<your-key> \
  lastfm-userbar
```

## Deployment

Automated deployment runs on push to `master` via GitHub Actions (`.github/workflows/deploy.yml`).

The pipeline:
1. Injects the Infisical SDK into the `ansible-core` virtualenv.
2. Installs Ansible collections from `ansible/requirements.yml`.
3. Loads `SSH_PRIVATE_KEY` from the `production` GitHub environment.
4. Runs `ansible-playbook -i ../inventory/hosts.yml deploy.yml` from the `ansible/` directory.

**Required GitHub Actions secrets** (in the `production` environment):

| Secret | Purpose |
|---|---|
| `SSH_PRIVATE_KEY` | SSH key for the target host |
| `INFISICAL_API_URL` | Infisical API endpoint |
| `INFISICAL_CLIENT_ID` | Infisical machine identity client ID |
| `INFISICAL_CLIENT_SECRET` | Infisical machine identity client secret |

Application secrets (`SECRET_KEY`, `LASTFM_API_KEY`) are pulled from Infisical at deploy time.

## License

MIT — see [LICENSE](LICENSE).
