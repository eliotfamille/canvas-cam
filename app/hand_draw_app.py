from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

from vision.camera import Camera
from vision.hand_tracker import HandTracker


class HandDrawApp(App):
    def build(self):
        self.camera = Camera(0)
        self.tracker = HandTracker()
        self.image = Image()
        self.texture = None  # cree a la premiere frame
        Clock.schedule_interval(self.update, 1 / 30)  # 30 FPS
        return self.image

    def update(self, dt):
        frame = self.camera.read()
        if frame is None:
            return

        hands = self.tracker.detect(frame)  # detection mains
        self.tracker.draw(frame, hands)  # dessin articulations

        h, w = frame.shape[:2]
        if self.texture is None:
            self.texture = Texture.create(size=(w, h), colorfmt="bgr")
            self.texture.flip_vertical()  # origine Kivy en bas a gauche
            self.image.texture = self.texture
        self.texture.blit_buffer(frame.tobytes(), colorfmt="bgr", bufferfmt="ubyte")  # envoi pixels
        self.image.canvas.ask_update()

    def on_stop(self):
        self.camera.release()
        self.tracker.close()
