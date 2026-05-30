FROM python:3.11-slim

WORKDIR /app

ARG SERVICE=backend

COPY backend/requirements.txt /tmp/backend-requirements.txt
COPY frontend/requirements.txt /tmp/frontend-requirements.txt

RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt -r /tmp/frontend-requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
