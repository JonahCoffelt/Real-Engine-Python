import sys
import pygame as pg
import moderngl as mgl
from graphics_engine import GraphicsEngine


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
        # Time variables
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        # MGL Context
        self.ctx = mgl.create_context()
        # Basic Gl setup
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        # Engine
        self.graphics_engine = GraphicsEngine(self)

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
            self.graphics_engine.scene.modify_terrain(0.2)

        if pg.mouse.get_pressed()[2] and self.mine_timer > self.mine_duration:
            self.mine_timer = 0
            self.graphics_engine.scene.modify_terrain(-.05)

    def start(self):
        self.run = True
        self.mine_timer = 0
        self.mine_duration = .04
        while self.run:
            pg.display.set_caption(str(round(self.clock.get_fps())))
            self.delta_time = self.clock.tick(60)
            self.mine_timer += self.delta_time / 1000
            self.check_events()  # Checks for window events
            self.graphics_engine.update(self.delta_time * 0.001)  # Render and update calls


if __name__ == '__main__':
    game = Game()
    game.start()