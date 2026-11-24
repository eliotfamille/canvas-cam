from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

from vision.camera import Camera


class HandDrawApp(App):
    def build(self):
        self.camera = Camera(0)
        self.image = Image()
        self.texture = None
        Clock.schedule_interval(self.update, 1 / 30)
        return self.image

    def update(self, dt):
        frame = self.camera.read()
        if frame is None:
            return

        h, w = frame.shape[:2]
        if self.texture is None:
            self.texture = Texture.create(size=(w, h), colorfmt="bgr")
            self.texture.flip_vertical()  # origine Kivy en bas a gauche
            self.image.texture = self.texture
        self.texture.blit_buffer(frame.tobytes(), colorfmt="bgr", bufferfmt="ubyte")
        self.image.canvas.ask_update()

    def on_stop(self):
        self.camera.release()
