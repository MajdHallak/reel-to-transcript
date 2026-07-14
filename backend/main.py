from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import whisper
import os
import ssl
import uuid

# Bypass SSL verification for the initial Whisper model download
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI(title="Reel Transcription API")

# Configure CORS to allow our React frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://reel-to-transcript.netlify.app"
    ],  # Adjust to our specific frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the expected JSON payload
class VideoRequest(BaseModel):
    url: str


@app.post("/api/transcribe")
async def transcribe_video(request: VideoRequest):
    # Generate a unique ID for temporary files to prevent cross-request collisions
    temp_id = str(uuid.uuid4())
    current_dir = os.path.dirname(os.path.abspath(__file__))
    download_template = os.path.join(current_dir, f"{temp_id}.%(ext)s")
    audio_filename = os.path.join(current_dir, f"{temp_id}.mp3")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": download_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(request.url, download=True)
            channel_name = (
                info_dict.get("uploader")
                or info_dict.get("channel")
                or "Unknown_Channel"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_filename)
        transcript = result["text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Ensure cleanup happens even if transcription fails
        if os.path.exists(audio_filename):
            os.remove(audio_filename)

    # Sanitize the channel name for file usage
    safe_channel_name = "".join(
        [c for c in channel_name if c.isalpha() or c.isdigit() or c == " "]
    ).rstrip()
    safe_channel_name = safe_channel_name.replace(" ", "_")

    return {"channel_name": safe_channel_name, "transcript": transcript}
