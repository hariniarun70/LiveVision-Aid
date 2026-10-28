from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO("yolov8n.pt")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    file = request.files['frame']
    img_bytes = file.read()


    npimg = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    h, w, _ = frame.shape

    results = model(frame)

    instructions = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            x1, y1, x2, y2 = box.xyxy[0]
            x_center = (x1 + x2) / 2
            width = x2 - x1

            # 🧭 POSITION
            if x_center < w * 0.4:
                pos = "left"
            elif x_center > w * 0.6:
                pos = "right"
            else:
                pos = "center"

            # 📏 DISTANCE
            if width > w * 0.5:
                dist = "very close"
            elif width > w * 0.3:
                dist = "close"
            else:
                dist = "far"

            # 🚦 NAVIGATION LOGIC
            if pos == "center" and dist in ["close", "very close"]:
                instructions.append(f"Stop, {label} ahead")

            elif pos == "left":
                instructions.append(f"{label} on your left, move right")

            elif pos == "right":
                instructions.append(f"{label} on your right, move left")

    if not instructions:
        instructions.append("Path is clear, go straight")

    final_text = ". ".join(instructions)

    print(final_text)

    return jsonify({"result": final_text})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)