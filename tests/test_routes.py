from io import BytesIO

from PIL import Image
import pytest

from app import create_app


def _png_bytes():
    buffer = BytesIO()
    Image.new("RGB", (16, 16), "#d4af37").save(buffer, format="PNG")
    return buffer.getvalue()


def _png_tuple(name):
    return (BytesIO(_png_bytes()), name, "image/png")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("config.STORAGE_DIR", tmp_path)
    monkeypatch.setattr("services.jobs.STORAGE_DIR", tmp_path)
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_dashboard_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Property title" in response.data
    assert b"Save listing job" in response.data


def test_generate_rejects_missing_images(client):
    response = client.post(
        "/generate",
        data={"title": "Test Home", "location": "Mumbai"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert b"at least 4" in response.data


def test_generate_saves_job_and_redirects(client):
    data = {
        "title": "Sea View Apartment",
        "location": "Goa",
        "price": "8500000",
        "images": [_png_tuple(f"{i}.png") for i in range(4)],
    }
    response = client.post("/generate", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    location = response.headers["Location"]
    assert "/jobs/" in location
    follow = client.get(location)
    assert follow.status_code == 200
    assert b"Sea View Apartment" in follow.data
    assert b"listing_saved" in follow.data


def test_json_validation_errors(client):
    response = client.post(
        "/generate",
        data={"title": "", "location": ""},
        headers={"Accept": "application/json"},
        content_type="multipart/form-data",
    )
    payload = response.get_json()
    assert response.status_code == 400
    assert payload["ok"] is False
    assert "title" in payload["errors"]
