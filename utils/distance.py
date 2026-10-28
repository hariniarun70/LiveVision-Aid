def estimate_distance(box):

    x1, y1, x2, y2 = box

    height = y2 - y1

    if height > 350:
        return "very close"

    elif height > 200:
        return "close"

    else:
        return "far"