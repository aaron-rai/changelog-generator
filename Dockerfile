FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy required files
COPY src /app/src
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set entrypoint
ENTRYPOINT ["python", "/app/src/generate_changelog.py"]