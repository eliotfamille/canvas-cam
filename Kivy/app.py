import math

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, InstructionGroup, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget

from Kivy.landmarks_view import LandmarksView
from Mediapipe.hand_tracker import HandTracker
from OpenCV.camera import Camera

ERASER_RADIUS = 40  # taille de l'eponge en pixels


class DrawWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = Camera()
        self.tracker = HandTracker()
        self.texture = None
        self.strokes = []  # tous les traits(x, y)
        self.stroke = None  # trait en cours
        self.line = None  # instruction graphique du trait en cours
        with self.canvas:
            Color(1, 1, 1, 1)
            self.image = Rectangle()  # image de la camra
        self.group = InstructionGroup()  # contient les traits rouges
        self.group.add(Color(1, 0, 0, 1))  # une seule couleur
        self.canvas.add(self.group)
        self.landmarks = LandmarksView()  # articulations, affiches par-dessus
        self.add_widget(self.landmarks)
        Clock.schedule_interval(self.update, 1 / 30)

    def update(self, dt):
        frame = self.camera.read()
        if frame is None:
            return

        h, w = frame.shape[:2]
        if self.texture is None:
            self.texture = Texture.create(size=(w, h), colorfmt="rgb")
            self.texture.flip_vertical()  # OpenCV haut en premier
            self.image.texture = self.texture
        self.texture.blit_buffer(frame.tobytes(), colorfmt="rgb", bufferfmt="ubyte")
        self.image.pos, self.image.size = self.pos, self.size
        self.landmarks.pos, self.landmarks.size = self.pos, self.size
        self.canvas.ask_update()  # force le redessin

        hand = self.tracker.detect(frame)
        self.landmarks.update(hand[0] if hand else None)
        if hand is None:
            self.stroke = self.line = None
            return
        p, gesture = hand
        point = p[9] if gesture == "erase" else p[8]  # centre du poing ou bout de l'index
        x, y = point.x * self.width, (1 - point.y) * self.height  # y inverse pour Kivy

        if gesture == "write":
            if self.stroke is None:  # nouveau trait
                self.stroke = [(x, y)]
                self.strokes.append(self.stroke)
                self.line = Line(points=[x, y], width=3)
                self.group.add(self.line)
            else:
                self.stroke.append((x, y))
                self.line.points += [x, y]
        else:
            self.stroke = self.line = None  # on arrete d'ecrire
            if gesture == "erase":
                self.erase(x, y)

    def erase(self, x, y):
        kept, changed = [], False
        for stroke in self.strokes:
            part = []
            for point in stroke:
                if math.dist(point, (x, y)) < ERASER_RADIUS:
                    changed = True  # point efface
                    if len(part) > 1:
                        kept.append(part)
                    part = []
                else:
                    part.append(point)
            if len(part) > 1:
                kept.append(part)
        if changed:  # on redessine seulement les morceaux restants
            self.strokes = kept
            self.group.clear()
            self.group.add(Color(1, 0, 0, 1))
            for stroke in kept:
                self.group.add(Line(points=[c for point in stroke for c in point], width=3))


class HandDrawApp(App):
    def build(self):
        self.widget = DrawWidget()
        return self.widget

    def on_stop(self):
        self.widget.camera.release()
        self.widget.tracker.close()
