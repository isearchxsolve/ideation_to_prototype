FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY src/ ./src/

# Add version label (can be overridden by build-arg)
ARG VERSION=0.1.0
LABEL version="${VERSION}"

EXPOSE 8000

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

# Healthcheck using the app's /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${APP_PORT}/health || exit 1

# Use non-root user for security
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

CMD ["python", "-m", "src.demo.app"]
