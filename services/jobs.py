"""Create isolated job folders and save uploads plus metadata."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.utils import secure_filename

from config import STORAGE_DIR


def new_job_id():
    return uuid.uuid4().hex[:12]


def job_path(job_id):
    return STORAGE_DIR / job_id


def create_job(listing, images, music_file=None):
    job_id = new_job_id()
    folder = job_path(job_id)
    images_dir = folder / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    saved_names = []
    for index, storage in enumerate(images, start=1):
        ext = Path(storage.filename).suffix.lower() or ".jpg"
        name = f"{index:02d}{ext}"
        destination = images_dir / name
        storage.stream.seek(0)
        storage.save(destination)
        saved_names.append(name)

    music_name = None
    if music_file is not None:
        original = secure_filename(music_file.filename) or "track"
        ext = Path(original).suffix.lower() or ".mp3"
        music_name = f"music{ext}"
        music_file.stream.seek(0)
        music_file.save(folder / music_name)

    provided = {key: value for key, value in listing.items() if value not in ("", None, False)}
    skipped = sorted(
        key
        for key, value in listing.items()
        if value in ("", None, False) and key not in ("voice_over", "use_background_music")
    )

    metadata = {
        "job_id": job_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "listing_saved",
        "phase": 1,
        "listing": listing,
        "provided_fields": sorted(provided.keys()),
        "skipped_fields": skipped,
        "images": saved_names,
        "music_file": music_name,
        "notes": "Video generation is not implemented yet. Listing and photos are stored for later phases.",
    }
    (folder / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return metadata


def load_job(job_id):
    folder = job_path(job_id)
    meta_file = folder / "metadata.json"
    if not meta_file.exists():
        return None
    return json.loads(meta_file.read_text(encoding="utf-8"))
