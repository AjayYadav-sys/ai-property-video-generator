from io import BytesIO

from PIL import Image
from werkzeug.datastructures import FileStorage

from app.validators import validate_images, validate_property_fields


def _image_storage(name="photo.png", fmt="PNG", size=(12, 12)):
    buffer = BytesIO()
    Image.new("RGB", size, "navy").save(buffer, format=fmt)
    buffer.seek(0)
    return FileStorage(stream=buffer, filename=name, content_type=f"image/{fmt.lower()}")


def test_requires_title_and_location():
    errors = validate_property_fields({"title": "", "location": ""})
    assert "title" in errors
    assert "location" in errors


def test_optional_numbers_can_be_blank():
    errors = validate_property_fields(
        {
            "title": "Lake House",
            "location": "Pune",
            "price": "",
            "bedrooms": "",
            "bathrooms": "",
            "area": "",
        }
    )
    assert errors == {}


def test_invalid_price_is_rejected():
    errors = validate_property_fields(
        {"title": "Lake House", "location": "Pune", "price": "not-a-number"}
    )
    assert "price" in errors


def test_too_few_images():
    errors, valid = validate_images([_image_storage() for _ in range(3)])
    assert "images" in errors
    assert len(valid) == 3


def test_accepts_four_valid_images():
    errors, valid = validate_images([_image_storage(f"{i}.png") for i in range(4)])
    assert errors == {}
    assert len(valid) == 4


def test_rejects_non_image_bytes():
    fake = FileStorage(stream=BytesIO(b"hello"), filename="note.png", content_type="image/png")
    errors, valid = validate_images([fake, _image_storage("a.png"), _image_storage("b.png"), _image_storage("c.png")])
    assert "images" in errors
    assert len(valid) == 3
