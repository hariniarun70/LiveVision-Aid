from ultralytics import YOLO
import cv2
import numpy as np

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # you can upgrade to yolov8s or yolov8m for better accuracy

# Minimum confidence threshold
CONFIDENCE_THRESHOLD = 0.5

def detect_objects(frame):
    """
    Run YOLO detection on a frame and return list of objects with label, box, and confidence.
    """
    # Optional: resize frame to YOLO expected size for speed and consistency
    input_frame = cv2.resize(frame, (640, 640))

    results = model(input_frame)  # runs detection

    objects = []

    for r in results:
        # YOLOv8 stores boxes in r.boxes
        for box in r.boxes:
            conf = float(box.conf[0])  # confidence score
            if conf < CONFIDENCE_THRESHOLD:
                continue  # skip low-confidence detections

            cls = int(box.cls[0])
            label = model.names[cls]

            # Convert YOLO coordinates to original frame scale
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            
            # If frame was resized, scale back to original frame size
            height_ratio = frame.shape[0] / input_frame.shape[0]
            width_ratio = frame.shape[1] / input_frame.shape[1]
            x1 = int(x1 * width_ratio)
            x2 = int(x2 * width_ratio)
            y1 = int(y1 * height_ratio)
            y2 = int(y2 * height_ratio)

            objects.append({
                "label": label,
                "box": [x1, y1, x2, y2],
                "confidence": conf
            })

    return objects