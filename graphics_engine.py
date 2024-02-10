import pygame as pg
from scene import Scene
from camera import Camera

class GraphicsEngine:
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx
        
        self.camera = Camera(self.app)
        self.scene  = Scene(self)

    def update(self):
        self.ctx.clear(color=(0.08, 0.16, 0.18))

        self.camera.update()
        self.scene.render()

        pg.display.flip()