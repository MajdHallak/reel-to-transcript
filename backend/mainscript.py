import yt_dlp
import whisper
import os
import ssl

# Bypass SSL verification for the initial Whisper model download
ssl._create_default_https_context = ssl._create_unverified_context


def get_reel_transcript(url):
    # Set up our absolute paths for downloading
    current_dir = os.path.dirname(os.path.abspath(__file__))
    download_template = os.path.join(current_dir, "temp_audio.%(ext)s")
    audio_filename = os.path.join(current_dir, "temp_audio.mp3")

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

    print("Downloading audio and fetching metadata...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info gets the video data as a dictionary while downloading
            info_dict = ydl.extract_info(url, download=True)

            # Retrieve the uploader name, falling back to a default if unavailable
            channel_name = (
                info_dict.get("uploader")
                or info_dict.get("channel")
                or "Unknown_Channel"
            ) + reel_url[-3:]
    except Exception as e:
        print(f"An error occurred during download: {e}")
        return

    print("Transcribing audio...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_filename)
        transcript = result["text"]
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return

    # Clean up the temporary audio file
    if os.path.exists(audio_filename):
        os.remove(audio_filename)

    # Sanitize the channel name to ensure it is a valid filename
    # This removes emojis, slashes, or special characters that could crash the file creation
    safe_channel_name = "".join(
        [c for c in channel_name if c.isalpha() or c.isdigit() or c == " "]
    ).rstrip()
    safe_channel_name = safe_channel_name.replace(" ", "_")

    # Create the text file path
    txt_filename = os.path.join(current_dir, f"{safe_channel_name}.txt")

    # Save the transcript to the text file
    try:
        # encoding="utf-8" is crucial here, as transcripts often contain special characters
        with open(txt_filename, "w", encoding="utf-8") as file:
            file.write(transcript)
        print(f"\nSuccess! Transcript saved to: {txt_filename}")
    except Exception as e:
        print(f"\nFailed to save text file: {e}")


# Execution
if __name__ == "__main__":
    reel_url = "https://www.facebook.com/reel/1657337778952282"
    get_reel_transcript(reel_url)
