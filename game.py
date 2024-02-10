import sys
import pygame as pg
import moderngl as mgl
from graphics_engine import GraphicsEngine

class Game:
    def __init__(self, win_size=(1600, 900)):
        pg.init()
        self.clock = pg.time.Clock()

        self.win_size = win_size

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode(self.win_size, flags=pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        self.graphics_engine = GraphicsEngine(self)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    pg.event.set_grab(False)
                    pg.mouse.set_visible(True)
            if event.type == pg.MOUSEBUTTONDOWN:
                pg.event.set_grab(True)
                pg.mouse.set_visible(False)

    def start(self):
        self.run = True
        while self.run:
            self.delta_time = self.clock.tick(120)
            self.check_events()
            self.graphics_engine.update()


if __name__ == '__main__':
    game = Game()
    game.start()