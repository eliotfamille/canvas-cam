import math
import time
from pathlib import Path

import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL = Path(__file__).parent / "hand_landmarker.task"


def finger_up(p, tip, pip):
    # si le bout est plus loin du poignet
    return math.dist((p[0].x, p[0].y), (p[tip].x, p[tip].y)) > math.dist((p[0].x, p[0].y), (p[pip].x, p[pip].y))


class HandTracker:
    def __init__(self):
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(MODEL)),
            running_mode=VisionRunningMode.VIDEO)
        self.landmarker = HandLandmarker.create_from_options(options)
        self.last_ms = -1

    def detect(self, rgb):
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ms = int(time.monotonic() * 1000)
        if ms <= self.last_ms:  # le timestamp doit toujours augmenter
            ms = self.last_ms + 1
        self.last_ms = ms
        result = self.landmarker.detect_for_video(image, ms)
        if not result.hand_landmarks:
            return None

        p = result.hand_landmarks[0]  # 21 points de la première main
        index = finger_up(p, 8, 6)
        others = [finger_up(p, 12, 10), finger_up(p, 16, 14), finger_up(p, 20, 18)]

        if index and not any(others):
            gesture = "write"  # seul l'index est tendu
        elif not index and not any(others):
            gesture = "erase"  # poing ferme
        else:
            gesture = "stop"
        return p, gesture  # les 21 points (x, y entre 0 et 1) et le geste

    def close(self):
        self.landmarker.close()