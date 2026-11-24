import cv2


class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv2.flip(frame, 1)  # effet miroir

    def release(self):
        self.cap.release()