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

## Screenshots

![Main screen](screenshots/Full%20View.PNG)
![Download progress in MB](screenshots/Download%20with%20progress%20and%20size%20in%20MB.PNG)

## Files
- [app.py](app.py): backend API + downloader
- [index.html](index.html): UI
- [script.js](script.js): frontend logic
- [style.css](style.css): styling
- [downloads/](downloads/): saved videos

## Notes
- Do not commit .venv or downloads. They are already ignored.
- If a pin has no audio, the downloaded file will also be silent.

## Shortcut
- You can also run the app with the provided `run.bat` file, which will set up the virtual environment and start the server for you. Just double-click it!
- Or you can create shortcut of bat file into your desktop to easy for opening the app.