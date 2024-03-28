import sys
import pygame as pg
import moderngl as mgl
from graphics_engine import GraphicsEngine
import glm
import numpy as np
import time

class Game:
    def __init__(self, win_size=(1600, 900)):
        # Pygame initialization
        pg.init()
        # Window size (resizable)
        self.win_size = win_size
        # GL Attributes
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # Pygame display init
        pg.display.set_mode(self.win_size, flags=pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
        # Lock mouse in place and hide
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        # MGL Context
        self.ctx = mgl.create_context()
        # Basic Gl setup
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        # Engine
        self.graphics_engine = GraphicsEngine(self)
        # Time variables
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:  # Unlock mouse
                    pg.event.set_grab(False)
                    pg.mouse.set_visible(True)
                
            if event.type == pg.MOUSEBUTTONDOWN:  # Lock mouse
                pg.event.set_grab(True)
                pg.mouse.set_visible(False)

        if pg.mouse.get_pressed()[0] and self.mine_timer > self.mine_duration:
            self.mine_timer = 0
            
            self.graphics_engine.scene.entity_handler.entities[0].spell.get_bullets(self.graphics_engine.scene.entity_handler.entities[0].obj.pos + self.graphics_engine.camera.forward*2, np.array([i for i in glm.normalize(self.graphics_engine.scene.entity_handler.entities[0].obj.pos - self.graphics_engine.camera.position)]))
            
            self.graphics_engine.scene.entity_handler.entities[0].spell = self.graphics_engine.scene.entity_handler.spell_handler.create_random_spell()

        if pg.mouse.get_pressed()[2] and self.mine_timer > self.mine_duration:
            self.mine_timer = 0

    def start(self):
        self.run = True
        self.mine_timer = 0
        self.mine_duration = 0.04
        while self.run:
            pg.display.set_caption(str(round(self.clock.get_fps())))
            self.delta_time = self.clock.tick()
            self.mine_timer += self.delta_time / 1000
            self.check_events()  # Checks for window events
            self.graphics_engine.update(self.delta_time * 0.001)  # Render and update calls

if __name__ == '__main__':
    game = Game()
    game.start()