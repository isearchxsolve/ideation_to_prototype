FROM python:3.11-slim

WORKDIR /app

COPY requirements-qa.txt .
RUN pip install --no-cache-dir -r requirements-qa.txt

COPY src/ ./src/

EXPOSE 8000

ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

CMD ["python", "-m", "src.demo.app"]
