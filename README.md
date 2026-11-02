# AI Property Video Generator

Flask web app for a student assignment: collect real-estate listing details and 4–8 property photos, validate them, and store a job folder. **Phase 1 does not render video yet.**

The script engine never invents facts. Blank fields are skipped.

## Phase 0–1 status

- Professional dark navy / gold dashboard
- Property details form
- 4–8 image upload, preview, remove, and reorder
- Frontend and backend validation
- Job folder + metadata saved under `storage/jobs/`
- Video, captions, voice-over, and FFmpeg are **not** implemented yet

## Requirements

- Windows 10/11
- Python 3.11 or newer
- FFmpeg is **not** required until a later phase

## Run locally

```powershell
cd "C:\Users\Aman Yadav\Desktop\Projects\ai-property-video-generator"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Tests

```powershell
.\venv\Scripts\activate
python -m pytest tests -q
```

## Notes

- Copy `.env.example` to `.env`. Do not commit `.env`.
- No API keys are needed.
- No login (local demo).
