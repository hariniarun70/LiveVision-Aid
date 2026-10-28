import cv2

net = cv2.dnn.readNetFromCaffe(
    "MobileNetSSD_deploy.prototxt",
    "MobileNetSSD_deploy.caffemodel"
)

def detect_indoor(frame):

    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300,300), 127.5)

    net.setInput(blob)

    detections = net.forward()

    objects = []

    for i in range(detections.shape[2]):

        confidence = detections[0,0,i,2]

        if confidence > 0.5:

            box = detections[0,0,i,3:7]

            h, w = frame.shape[:2]

            x1 = int(box[0] * w)
            y1 = int(box[1] * h)
            x2 = int(box[2] * w)
            y2 = int(box[3] * h)

            objects.append({
                "label": "object",
                "box": [x1, y1, x2, y2]
            })

    return objects