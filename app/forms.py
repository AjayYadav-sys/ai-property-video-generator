"""Read and clean property form fields. Empty values stay empty (never invented)."""

from flask import request


TEXT_FIELDS = (
    "title",
    "property_type",
    "location",
    "price",
    "currency",
    "bedrooms",
    "bathrooms",
    "area",
    "area_unit",
    "highlights",
    "description",
    "call_to_action",
)

PROPERTY_TYPES = (
    "",
    "Apartment",
    "House",
    "Villa",
    "Condo",
    "Townhouse",
    "Plot",
    "Other",
)

CURRENCIES = ("INR", "USD", "EUR", "GBP")
AREA_UNITS = ("sqft", "sqm")


def parse_property_form():
    data = {}
    for name in TEXT_FIELDS:
        value = (request.form.get(name) or "").strip()
        data[name] = value

    data["voice_over"] = request.form.get("voice_over") in ("on", "true", "1")
    data["use_background_music"] = request.form.get("use_background_music") in (
        "on",
        "true",
        "1",
    )
    if not data.get("price"):
        data["currency"] = ""
    if not data.get("area"):
        data["area_unit"] = ""
    return data
