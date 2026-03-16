# Swarm Deployment Runbook

## 1) Build images

```bash
docker build -t chicken-trader-backend:latest ./backend
docker build -t chicken-trader-frontend:latest ./frontend
```

## 2) Initialize swarm

```bash
docker swarm init
```

## 3) Prepare env

```bash
cp .env.example .env
# Fill API keys and credentials
```

## 4) Deploy stack

```bash
docker stack deploy -c docker-compose.network.yml chicken-trader
docker stack deploy -c docker-compose.network.yml -c docker-compose.app.yml -c docker-compose.urls-local.yml chicken-trader
```

## 5) Verify services

```bash
docker stack services chicken-trader
docker service logs chicken-trader_api
```

## Networking model

- `public` overlay: caddy ingress + frontend + api
- `private` overlay: api + worker + scheduler + postgres + redis
- Postgres and Redis are not published externally.

## Caddy label routing

- Frontend: `app.localhost`
- API: `api.localhost`

For production hostnames, deploy with:

```bash
docker stack deploy -c docker-compose.network.yml -c docker-compose.app.yml -c docker-compose.urls-prod.yml chicken-trader
```

Adjust hostnames in `docker-compose.urls-prod.yml` labels (or set `APP_HOST` / `API_HOST`) for real domains.
