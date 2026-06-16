# lastfm-userbar

Deploys the lastfm-userbar Flask app as a Docker container with nginx upstream and location config.

## What it does

- Creates the app directory on the remote host
- Syncs application code via rsync (excludes `ansible/`, `.git/`, `__pycache__/`)
- Builds a Docker image from the project's `Dockerfile` (only when code changed)
- Runs the container on the configured Docker network, injecting secrets as env vars
- Deploys nginx upstream and location config templates; reloads nginx on change

## Variables

Variables from `defaults/main.yml` (operator-overridable):

| Variable | Default | Description |
|---|---|---|
| `lastfm_userbar_container_name` | `lastfm-userbar` | Docker container name |
| `lastfm_userbar_image` | `lastfm-userbar` | Docker image name |
| `lastfm_userbar_port` | `8100` | Port the container listens on |
| `lastfm_userbar_app_dir` | `/opt/lastfm-userbar/app` | Remote code sync destination |
| `docker_volumes_directory` | `/opt/docker` | Root for Docker-managed volumes |
| `nginx_confd_path` | `{{ docker_volumes_directory }}/nginx/conf.d` | nginx `conf.d` directory |
| `nginx_custom_upstream_path` | `{{ nginx_confd_path }}/custom-upstream` | nginx upstream config directory |
| `nginx_docker_container_name` | `nginx-server` | Running nginx container name |

Variables required in inventory `group_vars` (not in defaults):

| Variable | Description |
|---|---|
| `lastfm_userbar_domain` | Domain name used to name nginx config files |
| `docker_network` | Docker network to attach the container to |

Secrets injected as container env vars at deploy time via Infisical:

| Infisical key | Container env var |
|---|---|
| `lastfm-shared-secret-lastfm-userbar` | `SECRET_KEY` |
| `lastfm-api-key-lastfm-userbar` | `LASTFM_API_KEY` |

## Usage

```bash
cd ansible
ansible-playbook -i inventories/zelgray.cherkasy.ua/ playbooks/deploy.yml
```

## Notes

- The Docker image is rebuilt only when rsync reports changes (`_sync.changed`).
- Nginx is reloaded via `docker exec nginx -s reload` rather than restarting the container.
- The role uses `become: yes` only for tasks that require root (file creation, Docker, nginx).
