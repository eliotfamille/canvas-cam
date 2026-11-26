import cv2 as cv

class Camera:
    def __init__(self, index=0):
        self.cap = cv.VideoCapture(index)  # ouverture webcam
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return cv.flip(frame, 1)  # effet miroir

    def release(self):
        self.cap.release()  # liberer camera
