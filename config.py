"""Application settings. No API keys are required for Phase 0–1."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

STORAGE_DIR = BASE_DIR / "storage" / "jobs"

MIN_IMAGES = 4
MAX_IMAGES = 8
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB per photo
MAX_MUSIC_BYTES = 15 * 1024 * 1024
MAX_CONTENT_LENGTH = (MAX_IMAGES * MAX_IMAGE_BYTES) + MAX_MUSIC_BYTES + (1 * 1024 * 1024)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIMES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
ALLOWED_MUSIC_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a"}

# Used in later phases; kept here so config stays in one place.
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
