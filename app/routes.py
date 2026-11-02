"""HTTP routes for the dashboard and listing upload."""

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from app.forms import AREA_UNITS, CURRENCIES, PROPERTY_TYPES, parse_property_form
from app.validators import merge_errors, validate_images, validate_music, validate_property_fields
from config import MAX_IMAGES, MIN_IMAGES
from services.jobs import create_job, job_path, load_job

bp = Blueprint("main", __name__)


def _wants_json():
    accept = request.headers.get("Accept", "")
    return "application/json" in accept or request.headers.get("X-Requested-With") == "XMLHttpRequest"


@bp.get("/")
def dashboard():
    return render_template(
        "dashboard.html",
        min_images=MIN_IMAGES,
        max_images=MAX_IMAGES,
        property_types=PROPERTY_TYPES,
        currencies=CURRENCIES,
        area_units=AREA_UNITS,
        values={},
        errors={},
    )


@bp.post("/generate")
def generate():
    listing = parse_property_form()
    field_errors = validate_property_fields(listing)
    image_errors, images = validate_images(request.files.getlist("images"))
    music_errors, music_file = validate_music(request.files.get("music"))
    errors = merge_errors(field_errors, image_errors, music_errors)

    if errors:
        if _wants_json():
            return {"ok": False, "errors": errors}, 400
        for messages in errors.values():
            for message in messages:
                flash(message, "error")
        return (
            render_template(
                "dashboard.html",
                min_images=MIN_IMAGES,
                max_images=MAX_IMAGES,
                property_types=PROPERTY_TYPES,
                currencies=CURRENCIES,
                area_units=AREA_UNITS,
                values=listing,
                errors=errors,
            ),
            400,
        )

    metadata = create_job(listing, images, music_file)
    if _wants_json():
        return {
            "ok": True,
            "redirect": url_for("main.job_detail", job_id=metadata["job_id"]),
        }
    return redirect(url_for("main.job_detail", job_id=metadata["job_id"]))


@bp.get("/jobs/<job_id>")
def job_detail(job_id):
    metadata = load_job(job_id)
    if metadata is None:
        abort(404)
    return render_template("result.html", job=metadata)


@bp.get("/jobs/<job_id>/images/<filename>")
def job_image(job_id, filename):
    metadata = load_job(job_id)
    if metadata is None or filename not in metadata.get("images", []):
        abort(404)
    return send_from_directory(job_path(job_id) / "images", filename)


@bp.get("/health")
def health():
    return {"ok": True, "phase": 1, "service": "ai-property-video-generator"}
