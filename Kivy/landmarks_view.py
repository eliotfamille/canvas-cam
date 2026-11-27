from kivy.graphics import Color, Point
from kivy.uix.widget import Widget


class LandmarksView(Widget):
    def update(self, landmarks):
        self.canvas.clear()
        if landmarks is None:  # pas de main
            return
        points = []
        for lm in landmarks:
            points += [lm.x * self.width, (1 - lm.y) * self.height]  # y inverse pour Kivy
        with self.canvas:
            Color(0, 1, 0, 1)
            Point(points=points, pointsize=5)  # un point par articulation