FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080 \
    APP_ROOT=/app

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY docs ./docs
COPY lawbench-opencompass ./lawbench-opencompass
COPY webapp ./webapp

RUN mkdir -p /app/outputs

EXPOSE 8080

CMD ["python", "backend/server.py"]
