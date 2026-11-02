"""Validate property details and uploaded images. Never invent missing values."""

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage

from app.errors import field_error
from app.forms import AREA_UNITS, CURRENCIES, PROPERTY_TYPES
from config import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_MUSIC_EXTENSIONS,
    MAX_IMAGE_BYTES,
    MAX_IMAGES,
    MAX_MUSIC_BYTES,
    MIN_IMAGES,
)


def _extension(filename):
    return Path(filename or "").suffix.lower()


def _is_filled_file(storage):
    if storage is None or not isinstance(storage, FileStorage):
        return False
    if not storage.filename or not str(storage.filename).strip():
        return False
    return True


def _positive_number(value, integer=False):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    if number < 0:
        return False
    if integer and not float(number).is_integer():
        return False
    return True


def validate_property_fields(data):
    errors = {}

    if not data.get("title"):
        field_error(errors, "title", "Property title is required.")
    elif len(data["title"]) > 120:
        field_error(errors, "title", "Title must be 120 characters or fewer.")

    if not data.get("location"):
        field_error(errors, "location", "Location is required.")
    elif len(data["location"]) > 160:
        field_error(errors, "location", "Location must be 160 characters or fewer.")

    property_type = data.get("property_type") or ""
    if property_type and property_type not in PROPERTY_TYPES:
        field_error(errors, "property_type", "Choose a valid property type.")

    if data.get("price") and not _positive_number(data["price"]):
        field_error(errors, "price", "Price must be a number 0 or greater, or left blank.")

    currency = data.get("currency") or ""
    if currency and currency not in CURRENCIES:
        field_error(errors, "currency", "Choose a valid currency.")

    if data.get("bedrooms") and not _positive_number(data["bedrooms"], integer=True):
        field_error(errors, "bedrooms", "Bedrooms must be a whole number, or left blank.")

    if data.get("bathrooms") and not _positive_number(data["bathrooms"]):
        field_error(errors, "bathrooms", "Bathrooms must be a number, or left blank.")

    if data.get("area") and not _positive_number(data["area"]):
        field_error(errors, "area", "Area must be a number 0 or greater, or left blank.")

    area_unit = data.get("area_unit") or ""
    if area_unit and area_unit not in AREA_UNITS:
        field_error(errors, "area_unit", "Choose a valid area unit.")

    if data.get("highlights") and len(data["highlights"]) > 1000:
        field_error(errors, "highlights", "Highlights must be 1000 characters or fewer.")

    if data.get("description") and len(data["description"]) > 4000:
        field_error(errors, "description", "Description must be 4000 characters or fewer.")

    if data.get("call_to_action") and len(data["call_to_action"]) > 200:
        field_error(errors, "call_to_action", "Call to action must be 200 characters or fewer.")

    return errors


def validate_images(files):
    errors = {}
    images = [item for item in files if _is_filled_file(item)]
    count = len(images)

    if count < MIN_IMAGES:
        field_error(
            errors,
            "images",
            f"Upload at least {MIN_IMAGES} property images (you sent {count}).",
        )
    if count > MAX_IMAGES:
        field_error(
            errors,
            "images",
            f"Upload at most {MAX_IMAGES} property images (you sent {count}).",
        )

    valid = []
    for index, storage in enumerate(images, start=1):
        ext = _extension(storage.filename)
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            field_error(
                errors,
                "images",
                f"Image {index} must be JPG, PNG, or WebP (got {ext or 'unknown'}).",
            )
            continue

        payload = storage.read()
        storage.stream.seek(0)
        if len(payload) == 0:
            field_error(errors, "images", f"Image {index} is empty.")
            continue
        if len(payload) > MAX_IMAGE_BYTES:
            field_error(
                errors,
                "images",
                f"Image {index} is larger than 10 MB.",
            )
            continue

        try:
            with Image.open(BytesIO(payload)) as picture:
                picture.verify()
        except (UnidentifiedImageError, OSError, ValueError):
            field_error(
                errors,
                "images",
                f"Image {index} is not a valid picture file.",
            )
            continue

        storage.stream.seek(0)
        valid.append(storage)

    return errors, valid


def validate_music(storage):
    errors = {}
    if not _is_filled_file(storage):
        return errors, None

    ext = _extension(storage.filename)
    if ext not in ALLOWED_MUSIC_EXTENSIONS:
        field_error(errors, "music", "Music must be MP3, WAV, OGG, or M4A.")
        return errors, None

    payload = storage.read()
    storage.stream.seek(0)
    if len(payload) == 0:
        field_error(errors, "music", "Music file is empty.")
        return errors, None
    if len(payload) > MAX_MUSIC_BYTES:
        field_error(errors, "music", "Music file is larger than 15 MB.")
        return errors, None

    storage.stream.seek(0)
    return errors, storage


def merge_errors(*error_maps):
    merged = {}
    for mapping in error_maps:
        for key, messages in mapping.items():
            merged.setdefault(key, []).extend(messages)
    return merged
