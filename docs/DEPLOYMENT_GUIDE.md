# FraudGuard AI — Enterprise Deployment & Production Guide

This guide outlines deployment strategies for FraudGuard AI across **Docker Compose**, **Standalone Containers**, and **Linux Bare-Metal / Virtual Machines (systemd + NGINX)**.

---

## 1. Quickstart with Docker Compose

The project includes a root `docker-compose.yml` orchestrating both the FastAPI backend and the React Vite frontend in isolated network namespaces.

### Running with Docker Compose:
```bash
# Clone repository
git clone <repo-url>
cd credit-card-fraud-demo

# Copy environment template
cp .env.example .env

# Build and start services in background
docker compose up -d --build

# View container logs
docker compose logs -f
```

- **Web Dashboard**: `http://localhost:5173` (or port 80 if reverse proxied)
- **FastAPI API & Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

## 2. Docker Architecture

### 2.1 Backend Dockerfile (`backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and artifacts
COPY . .

# Train model if artifacts missing
RUN python ml/train.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 Frontend Dockerfile (`frontend/Dockerfile`)
```dockerfile
# Build Stage
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production Stage (NGINX)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 3. Production Linux (systemd + NGINX) Deployment

### 3.1 Backend systemd Unit (`/etc/systemd/system/fraudguard-api.service`)
```ini
[Unit]
Description=FraudGuard AI FastAPI Backend
After=network.target

[Service]
User=fraudapp
Group=fraudapp
WorkingDirectory=/opt/fraudguard-ai/backend
EnvironmentFile=/opt/fraudguard-ai/.env
ExecStart=/opt/fraudguard-ai/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3.2 NGINX Reverse Proxy (`/etc/nginx/sites-available/fraudguard.conf`)
```nginx
server {
    listen 80;
    server_name fraudguard.internal.bank.com;

    # Frontend Static Assets
    location / {
        root /opt/fraudguard-ai/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API Routing
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /predict {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 4. Performance Tuning & High-Availability

1. **Uvicorn Concurrency**: For production load, deploy 4–8 Uvicorn worker processes (`--workers 4`) behind Gunicorn or NGINX load balancer.
2. **SQLite WAL Mode**: To maximize concurrent read throughput without write contention, execute:
   ```sql
   PRAGMA journal_mode=WAL;
   PRAGMA synchronous=NORMAL;
   ```
3. **Model Warm-Up**: Ensure the model is loaded into memory during lifespan startup before receiving live traffic.
