# Start from official Python 3.11 on Debian "slim"
# "slim" strips out compilers and docs we don't need (~150MB vs ~1GB)
FROM python:3.11-slim

# Set the working directory inside the container
# Every command after this runs from /app
WORKDIR /app

# Copy requirements first, install dependencies
# This layer gets cached — only rebuilds when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
# Listed explicitly so we control exactly what goes in the image
COPY ha_client.py .
COPY ollama_client.py .
COPY decision_log.py .
COPY webhook.py .
COPY jarvis.py .
COPY jarvis_bot.py .

# Default entry point — docker-compose will override this per service
CMD ["python", "webhook.py"]
