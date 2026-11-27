import cv2


class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # première camera

    def read(self):
        ok, frame = self.cap.read()
        if not ok:  # pas d'image
            return None
        frame = cv2.flip(frame, 1)  # miroir
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR vers RGB

    def release(self):
        self.cap.release()
