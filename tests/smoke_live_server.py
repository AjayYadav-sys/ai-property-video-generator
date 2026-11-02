"""One-off live-server check used during development. Safe to re-run."""

from io import BytesIO
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import uuid

from PIL import Image


def png_bytes(color):
    buffer = BytesIO()
    Image.new("RGB", (48, 36), color).save(buffer, format="PNG")
    return buffer.getvalue()


def main():
    print(urlopen("http://127.0.0.1:5000/health").read().decode())

    boundary = "----Boundary" + uuid.uuid4().hex
    parts = []
    for key, value in (("title", "Sea View Apartment"), ("location", "Goa"), ("price", "8500000")):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode()
        )
    for index, color in enumerate(((20, 40, 80), (40, 80, 120), (80, 120, 160), (200, 170, 80))):
        parts.append(
            (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"images\"; "
                f"filename=\"{index}.png\"\r\nContent-Type: image/png\r\n\r\n"
            ).encode()
        )
        parts.append(png_bytes(color))
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    request = Request("http://127.0.0.1:5000/generate", data=body, method="POST")
    request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    request.add_header("Accept", "application/json")
    try:
        response = urlopen(request)
        print("POST", response.status, response.read().decode())
    except HTTPError as error:
        print("POST ERR", error.code, error.read().decode())
        raise SystemExit(1)


if __name__ == "__main__":
    main()
