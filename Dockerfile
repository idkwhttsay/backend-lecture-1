FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY alembic.ini .
COPY migrate.py .
COPY nginx/ ./nginx/
COPY migrations/ ./migrations/

RUN python migrate.py migrate

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]