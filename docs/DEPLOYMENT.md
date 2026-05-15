# Deployment Guide

End-to-end instructions for deploying the system to a single VM running
Ubuntu 22.04+. The same blueprint works on Render, Fly.io, or any container
host – swap step 4 for your platform's equivalent.

## Architecture

```
[ Browser ] -> [ Nginx 80/443 ] -> /api -> [ Uvicorn :8000 (FastAPI) ] -> PostgreSQL
                                 -> /     -> static React build (SE1-Project/dist)
```

## 1. Prerequisites

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv build-essential nginx \
  postgresql postgresql-contrib nodejs npm git
```

## 2. PostgreSQL

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE trains;
CREATE USER trains_app WITH PASSWORD 'CHANGE_ME';
GRANT ALL PRIVILEGES ON DATABASE trains TO trains_app;
SQL
```

Capture the connection string for the next step:

```
postgresql://trains_app:CHANGE_ME@localhost:5432/trains
```

On Render, create a Render Postgres database and use its internal connection
string as the backend service's `DATABASE_URL`.

## 3. Backend

```bash
git clone <this-repo> /opt/trains && cd /opt/trains/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# environment
sudo tee /etc/trains.env >/dev/null <<EOF
DATABASE_URL=postgresql://trains_app:CHANGE_ME@localhost:5432/trains
CORS_ORIGINS=https://trains.example.com
SQL_ECHO=false
EOF
```

### systemd unit

```ini
# /etc/systemd/system/trains-api.service
[Unit]
Description=Train Reservation API
After=network.target postgresql.service

[Service]
Type=simple
EnvironmentFile=/etc/trains.env
WorkingDirectory=/opt/trains/backend
ExecStart=/opt/trains/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
User=www-data

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now trains-api
```

## 4. Frontend

```bash
cd /opt/trains/SE1-Project
npm ci
npm run build
sudo cp -r dist /var/www/trains
```

The frontend uses `VITE_API_BASE_URL`. For local development it falls back to
`http://127.0.0.1:8000/api`. For production, set it before building:

```bash
VITE_API_BASE_URL=https://api.trains.example.com/api npm run build
```

On Render Static Sites, set `VITE_API_BASE_URL` in the frontend service
environment variables and rebuild the frontend.

## Render quick setup

This repo includes a `render.yaml` Blueprint with:

- `train-system-api`: FastAPI backend.
- `train-system-web`: React static site.
- `train-system-db`: Render Postgres database.

If you use the Render dashboard manually instead, set these variables:

Backend service:

```env
DATABASE_URL=<Render Postgres internal connection string>
CORS_ORIGINS=https://your-frontend-service.onrender.com
SQL_ECHO=false
```

Frontend static site:

```env
VITE_API_BASE_URL=https://your-backend-service.onrender.com/api
```

After changing frontend environment variables on Render, trigger a new frontend
deploy so Vite bakes the new API URL into the static files.

## 5. Nginx reverse proxy

```nginx
# /etc/nginx/sites-available/trains
server {
    listen 80;
    server_name trains.example.com;

    root /var/www/trains;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/trains /etc/nginx/sites-enabled/trains
sudo nginx -t && sudo systemctl reload nginx
```

## 6. Bootstrap an admin user

```bash
curl -s -X POST http://127.0.0.1:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"root","email":"root@trains.example.com","password":"ChangeMe1","full_name":"Root","role":"admin"}'
```

## 7. Backups (Sprint 3 stretch / US-018)

Daily PostgreSQL dump to `/var/backups/trains/`:

```bash
sudo tee /etc/cron.d/trains-backup >/dev/null <<'CRON'
0 2 * * * postgres pg_dump -U trains_app -d trains \
  | gzip > /var/backups/trains/trains-$(date +\%F).sql.gz
CRON
```

Rotate to S3 / object storage from there (out of scope for Sprint 3).

## 8. CI/CD

The repository ships three GitHub Actions workflows:

* `.github/workflows/backend-ci.yml` – ruff + pytest on Python 3.11/3.12.
* `.github/workflows/frontend-ci.yml` – ESLint + Vitest + Vite build on
  Node 20/22, uploads `dist/` artifact for promotion.
* `.github/workflows/integration.yml` – boots the API and smoke-tests
  `/health` & `/openapi.json`.

Wire your deploy step into the workflows (e.g. `appleboy/ssh-action` to
`systemctl restart trains-api`) once you're ready to ship from `main`.

## Health checks

| Probe | URL |
|-------|-----|
| Liveness | `GET /health` |
| Readiness | `GET /` |
| OpenAPI | `GET /openapi.json` |
