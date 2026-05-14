FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

CMD ["sh", "-c", "python scripts/seed.py && gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 wsgi:app"]
