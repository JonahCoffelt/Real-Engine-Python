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
            self.mine_timer = 0
            
            self.graphics_engine.scene.entity_handler.entities[0].deck_handler.hand[self.graphics_engine.scene.ui_handler.values['selected_card']]\
                .get_bullets(self.graphics_engine.scene.entity_handler.entities[0].obj.pos + self.graphics_engine.camera.forward, np.array([i for i in glm.normalize(self.graphics_engine.camera.looking_at())]), self.graphics_engine.scene.entity_handler.entities[0].obj)
            
            self.graphics_engine.scene.entity_handler.entities[0].spell = self.graphics_engine.scene.entity_handler.spell_handler.create_random_spell()

    def start(self):
        self.run = True
        self.mine_timer = 0
        self.mine_duration = 0.04
        self.mouse_state = pg.mouse.get_pressed()
        while self.run:
            pg.display.set_caption(str(round(self.clock.get_fps())))
            self.delta_time = self.clock.tick()
            self.mine_timer += self.delta_time / 1000
            self.check_events()  # Checks for window events
            self.graphics_engine.update(self.delta_time * 0.001)  # Render and update calls

if __name__ == '__main__':
    game = Game()
    game.start()