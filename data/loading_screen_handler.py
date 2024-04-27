import sys
import pygame as pg
import moderngl as mgl
import numpy as np
from data.config import config
from data.text_handler import TextHandler
import random

vert_shader = """
#version 330 core

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;

out vec2 TexCoords;

void main()
{
    gl_Position = vec4(in_position.x, in_position.y, 0.0, 1.0); 
    TexCoords = in_texcoord_0;
}  
"""

frag_shader = """
#version 330 core
out vec4 fragColor;
  
in vec2 TexCoords;

uniform sampler2D UITexture;

void main()
{ 
    fragColor = texture(UITexture, vec2(TexCoords.x, -TexCoords.y));
    fragColor.rgb = fragColor.bgr;
}
"""

class LoadingScreen:
    def __init__(self, ctx, win_size):
        self.ctx = ctx
        self.win_size = win_size
        self.surf = pg.Surface(win_size).convert_alpha()
        self.text_handler = TextHandler()
        self.clock = pg.time.Clock()
        self.tex = None
        self.on_init()

    def on_init(self):
        # VBO        
        verticies = np.array([[-1, 1, 0], [-1, -1, 0], [ 1, -1, 0], [ 1, 1, 0], [-1, 1, 0], [ 1, -1, 0]], dtype='f4')
        uv = np.array([[0, 1], [0, 0], [1, 0], [1, 1], [0, 1], [1, 0]], dtype='f4')
        vertex_data = np.hstack([uv, verticies], dtype='f4')
        self.vbo = self.ctx.buffer(vertex_data)

        # Shader Program
        self.prog = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)

        # VAO
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '2f 3f', *['in_texcoord_0', 'in_position'])])

    def set_texture(self):
        if self.tex: self.tex.release()
        self.tex = self.ctx.texture(self.surf.get_size(), 4)
        self.tex.filter = (mgl.NEAREST, mgl.NEAREST)
        self.tex.swizzel = 'BGRA'
        self.tex.write(self.surf.get_view('1'))

    def update(self, text='Loading'):
        pg.display.set_caption(str(round(self.clock.get_fps())))
        self.delta_time = self.clock.tick()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        
        self.display(text)

    def display(self, text='Loading'):
        # Clear Screen
        self.ctx.clear(color=(0.08, 0.16, 0.18))

        # Make loading screen surface
        self.surf.fill((20, 20, 20))
        self.text_handler.render_text(self.surf, (0, 0, self.win_size[0], self.win_size[1]), text, size=48, center_height=True, center_width=True, color=(220, 220, 220))

        # Convert to texture and render
        self.set_texture()
        self.vao.program['UITexture'] = 0
        self.tex.use(location=0)
        self.vao.render()

        # Pygame disaplay
        pg.display.flip()

    def intro(self):
        time = 0
        pg_logo = pg.image.load('UI_Assets\python_logo.png').convert_alpha()
        logo_scale = self.win_size[1]/6
        pg_logo = pg.transform.scale(pg_logo, (logo_scale, logo_scale))
        while True:
            pg.display.set_caption(str(round(self.clock.get_fps())))
            time += self.clock.tick()/1000
            if time > 4: break
            if pg.mouse.get_pressed()[0]: break
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            if time < 2: opacity = time/2 * 255
            elif time > 3: opacity = (1 - (time - 3)) * 255

            # Clear Screen
            self.ctx.clear(color=(0.08, 0.16, 0.18))

            # Make loading screen surface
            self.surf.fill((20, 20, 20))
            pg_logo.set_alpha(opacity)
            self.surf.blit(pg_logo, (self.win_size[0]/2 - logo_scale/2, self.win_size[1]/2 - logo_scale/2))
            self.text_handler.render_text(self.surf, (0, 0, self.win_size[0], self.win_size[1] * 1.25), 'made with python', size=24, opacity=opacity, center_height=True, center_width=True, color=(220, 220, 220))
            self.text_handler.render_text(self.surf, (0, self.win_size[1]/8 * 7, self.win_size[0], self.win_size[1]/8), 'contians AI generated music', size=16, opacity=opacity, center_height=True, center_width=True, color=(220, 220, 220))

            # Convert to texture and render
            self.set_texture()
            self.vao.program['UITexture'] = 0
            self.tex.use(location=0)
            self.vao.render()

            # Pygame disaplay
            pg.display.flip()
    
    def get_card(self, card):
        time = 0
        while True:
            pg.display.set_caption(str(round(self.clock.get_fps())))
            dt = self.clock.tick()/1000
            time += dt
            if time > 4: break
            if pg.mouse.get_pressed()[0]: break
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            # Clear Screen
            self.ctx.clear(color=(0, 0, 0))

            # Make loading screen surface
            self.surf.fill((0, 0, 0, 0))

            for i in range(10):
                self.draw_beam((self.win_size[0]/2, self.win_size[1]/2), 40, time + i * (3.1415 * 2) / 10, .2, 300, color=(230, 230, 200), taper=1.5)
            for i in range(7):
                self.draw_beam((self.win_size[0]/2, self.win_size[1]/2), 60, -time * 1.5 + i * (3.1415 * 2) / 7, .1, 250, color=(250, 250, 230), taper=.75)
        
            # Convert to texture and render
            self.set_texture()
            self.vao.program['UITexture'] = 0
            self.tex.use(location=0)
            self.vao.render()

            # Pygame disaplay
            pg.display.flip()

    def destroy(self):
        self.vbo.release()
        self.tex.release()
        self.vao.release()