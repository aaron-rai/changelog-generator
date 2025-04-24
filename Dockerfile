FROM python:3.10-slim

WORKDIR /app

COPY src /app/src
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/app/src/generate_changelog.py"]