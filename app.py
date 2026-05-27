import requests
import json
from bs4 import BeautifulSoup
import re
import os
import threading
import uuid
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

app = Flask(__name__, static_folder=".", static_url_path="")

JOBS = {}


def get_video_url(pin_url):
    print(f"[*] Analyzing: {pin_url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }

    try:
        response = requests.get(pin_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[!] Error: Pinterest returned status {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Logic 1 : Look for json data in ld+json scripts
        ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
        for script in ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list): data = data[0]
                
                if "contentUrl" in data:
                    url = data["contentUrl"]
                    if ".mp4" in url:
                        return url
            except:
                continue

        # Logic 2 : If that fails, scan the raw HTML for video links
        print("[*] LD+JSON failed. Scanning raw source code...")
        match = re.search(r'https://v1\.pinimg\.com/videos/mc/exp/[^"]+\.mp4', response.text)
        if match:
            return match.group(0)

        return None

    except Exception as e:
        print(f"[!] Technical Failure: {e}")
        return None

def sanitize_filename(name):
    safe = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (" ", ".", "_", "-")]).strip()
    return safe or "untitled_pin"


def download_video(url, custom_name, target_dir, progress):
    if not custom_name.strip():
        custom_name = "untitled_pin"

    if not custom_name.endswith(".mp4"):
        custom_name += ".mp4"

    clean_name = sanitize_filename(custom_name)
    file_path = os.path.join(target_dir, clean_name)

    print(f"[*] Starting download: {clean_name}")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        progress["total"] = total
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress["downloaded"] += len(chunk)

    print(f"[✔] Success! Saved as: {file_path}")
    return file_path


def run_job(job_id, url, name):
    job = JOBS[job_id]
    try:
        video_link = get_video_url(url)
        if not video_link:
            job["status"] = "error"
            job["error"] = "Could not find a video link."
            return

        saved_path = download_video(video_link, name, DOWNLOADS_DIR, job)
        job["status"] = "done"
        job["file"] = os.path.basename(saved_path)
    except Exception as exc:
        job["status"] = "error"
        job["error"] = str(exc)


@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.post("/api/download")
def api_download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    name = (data.get("name") or "pinterest_video").strip()

    if not url:
        return jsonify({"ok": False, "error": "Missing URL."}), 400

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "downloading",
        "downloaded": 0,
        "total": 0,
        "file": "",
        "error": "",
    }

    thread = threading.Thread(target=run_job, args=(job_id, url, name), daemon=True)
    thread.start()

    return jsonify({"ok": True, "job_id": job_id})


@app.get("/api/status/<job_id>")
def api_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"status": "error", "error": "Job not found."}), 404

    return jsonify(job)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)