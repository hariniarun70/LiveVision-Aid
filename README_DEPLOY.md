# LiveVision Aid — deployment notes

## What this project contains
- Flask web application: `webapp.py`
- YOLOv8 model weights: `yolov8n.pt`
- Browser camera and voice interface: `templates/index.html`, `static/script.js`

## Deploy with GitHub + Render
1. Upload the contents of this folder to a GitHub repository.
2. In Render, choose **New + → Web Service** and connect that repository.
3. Render should detect `render.yaml`. If it does not, set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT webapp:app`
4. Deploy and open the HTTPS URL Render gives you.

## Important
- GitHub stores the code; Render runs the Flask/YOLO server. GitHub Pages alone cannot run this Python backend.
- The browser camera requires HTTPS (or localhost). Use the Render HTTPS URL on your phone.
- Free hosting may sleep, have limited memory, or process YOLO frames slowly. The first request can take time while the service starts.
- This is a prototype, not a safety-certified navigation device. Do not rely on it as the only mobility aid.
