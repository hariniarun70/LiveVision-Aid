import numpy as np

def detect_scene(frame):

    brightness = np.mean(frame)

    if brightness < 90:
        return "indoor"
    else:
        return "outdoor"