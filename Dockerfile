FROM python:3.12.3-slim

RUN mkdir -p /app
VOLUME ["/storage"]

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE ${PORT:-8000}

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} app:app"]
