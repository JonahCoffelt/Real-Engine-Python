import sys
import pygame as pg
import moderngl as mgl
from graphics_engine import GraphicsEngine
import glm
import numpy as np
from config import config
import cudart

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
        # MGL Context
        self.ctx = mgl.create_context()
        print(self.ctx.viewport)
        # Basic Gl setup
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        # Engine
        self.graphics_engine = GraphicsEngine(self)
        # Time variables
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0

    def check_events(self):
        self.events = pg.event.get()
        self.mouse_state = pg.mouse.get_pressed()
        for event in self.events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.VIDEORESIZE:
                self.ctx.viewport = (0, 0, event.w, event.h)
        
        self.graphics_engine.scene.ui_handler.get_events(self.events)

        if not config['runtime']['simulate']: return
        if self.mouse_state[0] and not self.graphics_engine.scene.ui_handler.mouse_buttons[0]:
            
            self.graphics_engine.scene.entity_handler.entities[0].use_card(self.graphics_engine.scene.ui_handler.values['selected_card'])

    def start(self):
        self.run = True
        self.mouse_state = pg.mouse.get_pressed()
        while self.run:
            pg.display.set_caption(str(round(self.clock.get_fps())))
            self.delta_time = self.clock.tick()
            self.check_events()  # Checks for window events
            self.graphics_engine.update(self.delta_time * 0.001)  # Render and update calls

if __name__ == '__main__':
    game = Game()
    game.start()