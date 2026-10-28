from flask import Flask, render_template, Response, request, send_from_directory
import cv2
import time
import threading
import numpy as np
from collections import deque

from outdoor.yolo_detection import detect_objects
from utils.direction import get_direction
from utils.speech import speak  # Laptop TTS

app = Flask(__name__, template_folder="templates")

# Laptop camera (optional)
cap = cv2.VideoCapture(0)

# 🔊 TTS and detection control
last_spoken_time = 0
speech_delay = 3
last_message = ""

# Detection aggregation
FRAME_HISTORY = 3
detection_history = deque(maxlen=FRAME_HISTORY)
CONFIDENCE_THRESHOLD = 0.5


# -------------------------------
# Laptop TTS (non-blocking)
# -------------------------------
def speak_async(msg):
    """Server-side TTS for laptop"""
    threading.Thread(target=speak, args=(msg,)).start()


# -------------------------------
# Detection logic with aggregation
# -------------------------------
def process_logic(objects, frame):
    global detection_history

    # Filter objects by confidence
    objects = [obj for obj in objects if obj.get("confidence", 1) >= CONFIDENCE_THRESHOLD]

    detection_history.append(objects)

    # Aggregate: keep only objects seen in multiple frames
    aggregated_counts = {}
    for frame_objs in detection_history:
        for obj in frame_objs:
            aggregated_counts[obj["label"]] = aggregated_counts.get(obj["label"], 0) + 1

    # Stable objects
    stable_objects = [obj for obj in objects if aggregated_counts[obj["label"]] >= (FRAME_HISTORY // 2 + 1)]

    # Build message
    message_parts = []
    path_blocked = False

    for obj in stable_objects[:5]:
        label = obj["label"]
        x1, y1, x2, y2 = obj["box"]

        area = (x2 - x1) * (y2 - y1)
        distance = "far"
        if area > 50000:
            distance = "very close"
        elif area > 20000:
            distance = "near"

        direction = get_direction(obj["box"], frame.shape[1])

        if direction == "ahead" and area > 20000:
            path_blocked = True

        # Immediate danger warning
        if label in ["car", "bus"] and distance == "very close":
            return f"Danger! {label} very close {direction}"

        message_parts.append(f"{label} {distance} {direction}")

    if path_blocked:
        return "Warning! Obstacle ahead. " + ", ".join(message_parts[:2])

    return ", ".join(message_parts[:3]) if message_parts else "Path is clear"


# -------------------------------
# Laptop camera streaming
# -------------------------------
def generate_frames():
    global last_spoken_time, last_message

    while True:
        success, frame = cap.read()
        if not success:
            break

        objects = detect_objects(frame)
        message = process_logic(objects, frame)

        # Laptop TTS
        current_time = time.time()
        if message != last_message and current_time - last_spoken_time > speech_delay:
            speak_async(message)
            last_spoken_time = current_time
            last_message = message

        # Draw boxes
        for obj in objects:
            x1, y1, x2, y2 = obj["box"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# Mobile detection API
@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return "No image received", 400

    file = request.files['image']
    file_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        return "Frame error", 400

    objects = detect_objects(frame)
    message = process_logic(objects, frame)

    # No server-side TTS for mobile; browser handles it
    return message


# Serve static CSS & JS
@app.route('/style.css')
def style():
    return send_from_directory("templates", "style.css")


@app.route('/script.js')
def script():
    return send_from_directory("templates", "script.js")


# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)