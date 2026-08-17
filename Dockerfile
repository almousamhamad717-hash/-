FROM python:3.11-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
