import os
import time

import cv2 as cv
import mediapipe as mp

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "hand_landmarker.task"  # modele telecharge
)

CONNECTIONS = [  # os de la main (indices des 21 landmarks)
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]


class HandTracker:
    def __init__(self, num_hands=2):
        self.latest = []  # dernier resultat recu

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,  # mode synchrone
            num_hands=num_hands,
            # result_callback=self._on_result,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.t0 = time.monotonic()
        self.last_ts = -1

    def _on_result(self, result, output_image, timestamp_ms):
        self.latest = result.hand_landmarks  # appele dans un autre thread, stocker seulement

    def detect(self, frame_bgr):
        rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)  # MediaPipe veut du RGB
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts = int((time.monotonic() - self.t0) * 1000)
        ts = max(ts, self.last_ts + 1)  # timestamps strictement croissants
        self.last_ts = ts
        # self.landmarker.detect_async(mp_image, ts)
        # return self.latest
        return self.landmarker.detect_for_video(mp_image, ts).hand_landmarks

    def draw(self, frame, hands):
        h, w = frame.shape[:2]
        for hand in hands:
            pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand]  # normalise vers pixels
            for a, b in CONNECTIONS:
                cv.line(frame, pts[a], pts[b], (0, 255, 0), 2)
            for p in pts:
                cv.circle(frame, p, 5, (0, 0, 255), -1)

    def close(self):
        self.landmarker.close()
