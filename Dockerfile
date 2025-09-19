FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/crawler /app/backend

EXPOSE 1239

ENV PYTHONPATH=/app
ENV FLASK_APP=backend/app.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=1239"]