from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from yt_dlp import YoutubeDL

# ---------- Setup ----------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- Pydantic model ----------
class DownloadRequest(BaseModel):
    url: str

# ---------- Routes ----------
@app.get("/")
def serve_home():
    return {"message": "Welcome to the Video Downloader API"}

@app.get("/files/{filename}")
def serve_file(filename: str):
    path = os.path.join(DOWNLOAD_DIR, filename)

    if not os.path.exists(path):
        return {"status": "error", "message": "File not found"}

    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.post("/download")
def download_video(data: DownloadRequest):
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

        # yt-dlp options
        ydl_opts = {
            "format": "mp4",
            "outtmpl": output_template,
            "quiet": False
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=True)
            filename = f"{file_id}.{info['ext']}"

        return {
            "status": "success",
            "title": info.get("title"),
            "platform": info.get("extractor_key"),
            "thumbnail": info.get("thumbnail"),
            "download_url": f"http://127.0.0.1:8000/files/{filename}"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
