# Pinterest Video Downloader

Small web app that lets you paste a Pinterest video link and download it with progress shown in the browser.

## What you need
- Python 3.10+

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python app.py
```

Open the app in your browser:

http://127.0.0.1:5000

## Files
- [app.py](app.py): backend API + downloader
- [index.html](index.html): UI
- [script.js](script.js): frontend logic
- [style.css](style.css): styling
- [downloads/](downloads/): saved videos

## Notes
- Do not commit .venv or downloads. They are already ignored.
- If a pin has no audio, the downloaded file will also be silent.
