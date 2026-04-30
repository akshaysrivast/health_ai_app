FROM python:3.11-slim

WORKDIR /app

COPY agents/feature-agent/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
EXPOSE 8000

WORKDIR /app/agents/feature-agent
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
