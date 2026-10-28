import cv2
import time
from deep_sort_realtime.deepsort_tracker import DeepSort

from outdoor.yolo_detection import detect_objects
from utils.direction import get_direction
from utils.distance import estimate_distance
from utils.speech import speak

speak("Blind assistant started. Scanning surroundings.")

cap = cv2.VideoCapture(0)

tracker = DeepSort(max_age=5)

last_spoken_time = 0
speech_delay = 3

prev_positions = {}

important_objects = [
    "person", "car", "bus", "truck",
    "motorcycle", "bicycle", "chair",
    "bench", "traffic light"
]

danger_objects = ["car", "bus", "truck", "motorcycle", "bicycle"]

while True:

    ret, frame = cap.read()
    if not ret:
        break

    objects = detect_objects(frame)

    detections = []

    for obj in objects:
        label = obj["label"]
        box = obj["box"]

        if label not in important_objects:
            continue

        x1, y1, x2, y2 = box
        w = x2 - x1
        h = y2 - y1

        detections.append(([x1, y1, w, h], 1.0, label))

    tracks = tracker.update_tracks(detections, frame=frame)

    best_message = None

    for track in tracks:

        if not track.is_confirmed():
            continue

        track_id = track.track_id
        l, t, w, h = map(int, track.to_ltrb())

        label = track.get_det_class()

        direction = get_direction([l, t, w, h], frame.shape[1])
        distance = estimate_distance([l, t, w, h])

        center_x = (l + w) // 2

        # movement detection
        movement = "stable"
        if track_id in prev_positions:
            prev_x = prev_positions[track_id]

            if center_x > prev_x + 10:
                movement = "moving right"
            elif center_x < prev_x - 10:
                movement = "moving left"

        prev_positions[track_id] = center_x

        # smart message selection
        if label in danger_objects and movement != "stable":
            message = f"Warning. {label} {movement}"
        elif direction == "ahead":
            message = f"Obstacle ahead. {label}"
        else:
            message = f"{label} on your {direction}"

        print(message)

        # pick only ONE message (priority)
        if best_message is None:
            best_message = message

        # draw box
        cv2.rectangle(frame, (l, t), (w, h), (0, 255, 0), 2)
        cv2.putText(frame, label, (l, t - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # speak only once
    current_time = time.time()
    if best_message and current_time - last_spoken_time > speech_delay:
        speak(best_message)
        last_spoken_time = current_time

    cv2.imshow("Blind Assistant Camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()