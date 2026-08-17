# Deployment Guide

How to build, run, and operate the demo application and the QA suite in
production-like environments.

## 1. Build the image

```bash
docker build --build-arg VERSION=1.0.0 -t demo-app:1.0.0 .
```

The image:

- runs as a non-root user (`appuser`),
- exposes port `8000`,
- includes a `HEALTHCHECK` against `/health` (30s interval, 3 retries),
- carries a `version` label for traceability.

## 2. Run with Docker

```bash
docker run -d --name demo-app \
  -p 8000:8000 \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  demo-app:1.0.0
```

Verify:

```bash
curl http://localhost:8000/health     # {"status":"ok",...}
curl http://localhost:8000/api/status # {"healthy":true,"version":"1.0.0"}
docker inspect --format='{{.State.Health.Status}}' demo-app
```

## 3. Kubernetes

Example manifests (adjust namespace, resources, and replica count):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
spec:
  replicas: 2
  selector:
    matchLabels: {app: demo-app}
  template:
    metadata:
      labels: {app: demo-app}
    spec:
      containers:
        - name: demo-app
          image: registry.example.com/demo-app:1.0.0
          ports: [{containerPort: 8000}]
          env:
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef: {name: demo-app-secrets, key: secret-key}
          readinessProbe:
            httpGet: {path: /health, port: 8000}
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet: {path: /health, port: 8000}
            initialDelaySeconds: 15
            periodSeconds: 20
          resources:
            requests: {cpu: 100m, memory: 128Mi}
            limits: {cpu: 500m, memory: 256Mi}
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app
spec:
  selector: {app: demo-app}
  ports: [{port: 80, targetPort: 8000}]
```

Store `SECRET_KEY` in a Kubernetes Secret, never in the manifest:

```bash
kubectl create secret generic demo-app-secrets \
  --from-literal=secret-key="$(openssl rand -hex 32)"
```

## 4. Configuration

All configuration is validated at startup by `src/demo/config.py`
(Pydantic Settings). Invalid values fail fast with a clear error.

| Variable | Default | Notes |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Set `0.0.0.0` inside containers (Dockerfile does this) |
| `APP_PORT` | `8000` | 1–65535 |
| `APP_DEBUG` | `false` | Keep `false` in production |
| `SECRET_KEY` | — | **Must be overridden** in any real deployment |

A `.env` file is supported for local development; do not ship it in images.

## 5. Running the QA suite against a deployment

```bash
pip install -r requirements-qa.txt
APP_BASE_URL=http://staging.example.com pytest --qa-suite=smoke
```

Reports land in `reports/` (HTML, JUnit XML, per-test JSON, failure
screenshots). CI uploads them as artifacts on every push/PR.

## 6. Rollback

Deployments are immutable, versioned images — rollback means redeploying
the previous tag:

```bash
# Docker
docker pull registry.example.com/demo-app:0.9.0
docker run -d -p 8000:8000 ... registry.example.com/demo-app:0.9.0

# Kubernetes
kubectl rollout undo deployment/demo-app
kubectl rollout status deployment/demo-app
```

Because state is in-memory per process, no data migration is needed when
rolling back; clients simply reconnect to the new (old) instance.

## 7. Observability

- **Health:** `GET /health` returns JSON with live user/message counts.
- **Version:** `GET /api/status` reports the app version.
- **Test evidence:** `reports/` from CI contains HTML report, JUnit XML,
  per-test JSON, and screenshots on failure — retain these as release
  audit artifacts.

## 8. Security checklist

- [ ] `SECRET_KEY` injected from a secret manager, not baked into the image
- [ ] Image runs as non-root (default in the Dockerfile)
- [ ] `pip-audit` gate green in CI (dependency vulnerabilities)
- [ ] Secret-scan gate green in CI (no hardcoded credentials)
- [ ] TLS termination at the ingress/load balancer (the app itself is HTTP)
- [ ] Network policies restrict ingress to the service port only
