FROM python:3.11-slim

# Install system dependencies required by Whisper and yt-dlp
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-load the Whisper base model so it doesn't download on the first request
RUN python -c "import whisper; whisper.load_model('base')"

COPY . .

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]