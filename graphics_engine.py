import pygame as pg
from scene import Scene
from camera import *
import cudart


class GraphicsEngine:
    def __init__(self, app) -> None:
        self.app = app
        self.ctx = app.ctx

        self.oninit()

    def oninit(self):
        
        # creates freecam and scene
        self.camera = Camera(self.app)
        self.scene  = Scene(self)
        
        # creates attached cam to scene object
        # self.camera = FollowCamera(self.app, self.scene.entity_handler.entities[0].obj)
        # self.scene.set_camera(self.camera)

    def update(self, delta_time):
        self.ctx.clear(color=(0.08, 0.16, 0.18))

        self.camera.update()  # Checks inputs and updates camera view matrix
        self.scene.render(delta_time)

        pg.display.flip()