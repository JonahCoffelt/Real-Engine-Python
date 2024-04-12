import pygame as pg
import numpy as np
import random
import moderngl as mgl
from config import config
from text_handler import TextHandler
import cudart


assets = {'btn_blank' : 'button_blank.png',
          'btn' : 'button.png'}


def surf_to_texture(ctx, surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (mgl.NEAREST, mgl.NEAREST)
    tex.swizzel = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex


class UI_Handler:
    def __init__(self, ctx, frame_vao, win_size=(900, 600)):
        self.ctx = ctx
        self.win_size = win_size
        self.text_handler = TextHandler()

        self.frame_vao = frame_vao
        self.surf = pg.Surface(win_size).convert_alpha()

        self.assets = {asset : pg.image.load(f'UI_Assets/{assets[asset]}').convert_alpha() for asset in assets}

        self.screen = self.main_menu

        self.update_texture = 2

        self.values = {'slider_test' : 2.0}

        self.buttons = {
        #   self.screen    : [pos/scale, img, function, *args]
        #   set pos/scale[2 or 3] = 0 to maintain original img shape and scale along other axis
            self.main_menu : [(np.array([.5, .3,  0, .1]), self.assets['btn'], self.set_screen, [self.hud]), 
                              (np.array([.5, .5,  0, .1]), self.assets['btn'], self.log, ['btn']), 
                              (np.array([.5, .7,  0, .1]), self.assets['btn'], self.add_button, ["rndm", self.assets['btn_blank'], self.log, ['Pop Up']]),
                              (np.array([.5, .1,  0, .1]), self.assets['btn_blank'], None, [])],
            self.hud : [(np.array([.1, .1, 0, .05]), self.assets['btn'], self.set_screen, [self.main_menu])]
        }

        self.text_boxes = {
            self.main_menu : [(np.array([.1, .1,  .1, .1]), self.assets['btn'], ('Red', 'default', 16, (255, 255, 255), (255, 0, 0, 255), True, True)), 
                              (np.array([.1, .3,  .1, .1]), self.assets['btn'], ('Green', 'default', 16, (255, 255, 255), (0, 255, 0, 255), True, True)), 
                              (np.array([.1, .5,  .1, .1]), self.assets['btn'], ('Blue', 'default', 16, (255, 255, 255), (0, 0, 255, 255), True, True)), 
                
                              (np.array([.5, .3,  0, .1]), self.assets['btn'], ('Text', 'default', 16, (255, 255, 255), (0, 0, 0, 100), True, True)),
                              (np.array([.5, .5,  0, .1]), self.assets['btn'], ('Text', 'default', 16, (255, 255, 255), (0, 0, 0, 100), True, True)), 
                              (np.array([.5, .7,  0, .1]), self.assets['btn'], ('Text', 'default', 16, (255, 255, 255), (0, 0, 0, 100), True, True)),
                              (np.array([.5, .1,  0, .1]), self.assets['btn_blank'], ('Text', 'default', 16, (255, 255, 255), (0, 0, 0, 100), True, True)),
                              (np.array([.2, .2, .3, .3]), None, ('You Can also just have your paragraphs line up agasint the top and left side rather than being centered.', 'default', 16, (255, 255, 255), (0, 0, 0, 100), False, False))],
            self.hud : []
        }

        self.sliders = {
            self.main_menu : [[np.array([.5, .9, .4, .05]), np.array([50, 150, 255]), (0, 10, 0.5), 'slider_test']],
            self.hud : []
        }

        self.hotkeys = {
            self.main_menu : {
                pg.K_ESCAPE : [[self.set_screen, [self.hud]], [self.set_attrib, ['runtime', 'simulate', True]]],
                pg.K_e : [[self.log, ['Pressed "E"']]]
            },
            self.hud : {
                pg.K_ESCAPE : [[self.set_screen, [self.main_menu]], [self.set_attrib, ['runtime', 'simulate', False]]],
                pg.K_e : [[self.log, ['Pressed "E"']]]
            }
        }

        self.current_buttons = self.buttons[self.main_menu][:]
        self.current_text_boxes = self.text_boxes[self.main_menu][:]
        self.current_sliders = self.sliders[self.main_menu][:]

        self.mouse_states = [False, False, False]
        self.key_states = pg.key.get_pressed()

        self.n_cards = 5

    def update(self):
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_buttons = pg.mouse.get_pressed()
        self.keys = pg.key.get_pressed()

        for key in self.hotkeys[self.screen]:
            if self.keys[key] and not self.key_states[key]: 
                for command in self.hotkeys[self.screen][key]: command[0](*command[1])

        self.screen()

        if self.update_texture >= 0: self.update_texture -= 1

        self.mouse_states = [state for state in self.mouse_buttons]
        self.key_states = self.keys

        if self.update_texture == 0 or self.update_texture == 1: self.render()


    def render(self):
        self.frame_vao.program['UITexture'] = 5
        surf_to_texture(self.ctx, self.surf).use(location=5)

    def set_attrib(self, category, var, value):
        config[category][var] = value

    def log(self, txt=''):
        print(txt)
        self.update_texture = 2

    def set_screen(self, screen):
        if screen in [self.main_menu]:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
        elif screen in [self.hud]:
            pg.event.set_grab(True)
            pg.mouse.set_visible(False) 

        self.update_texture = 2
        self.screen = screen
        self.current_buttons = self.buttons[screen][:]
        self.current_text_boxes = self.text_boxes[screen][:]
        self.current_sliders = self.sliders[screen][:]
    
    def add_button(self, pos: tuple=(.5, .5, .1, .1), img: pg.image=None, func=None, args: list=[]):
        if pos == "rndm": pos = np.array([random.uniform(0, 1), random.uniform(0, 1), .1, .1])
        self.current_buttons.append([np.array([*pos]), img, func, [*args]])

    def get_rect(self, element):
        win_scale = np.array([self.win_size[0], self.win_size[1], self.win_size[0], self.win_size[1]])
        rect = (element[0] * win_scale)
        rect[0] -= rect[2]/2
        rect[1] -= rect[3]/2

        if 0.0 in rect[2:]:
            index = np.where(rect==0.0)[0][0]
            img_rect = element[1].get_rect()
            if index == 2:
                rect[2] = rect[3] * (img_rect[2] / img_rect[3])
                rect[0] -= rect[2]/2
            if index == 3:
                rect[3] = rect[2] * (img_rect[3] / img_rect[2])
                rect[1] -= rect[3]/2
        
        return rect

    def draw_sliders(self, sliders):
        for slider in sliders:
            rect = self.get_rect(slider)
            if self.mouse_buttons[0]:
                if (rect[0] < self.mouse_pos[0] < rect[0] + rect[2] and rect[1] < self.mouse_pos[1] < rect[1] + rect[3]):
                    self.values[slider[3]] = min(max(((self.mouse_pos[0] - rect[0] + rect[3]/4) / rect[2]) * slider[2][1], slider[2][0]), slider[2][1])
                    self.values[slider[3]] -= self.values[slider[3]] % slider[2][2]
                    self.update_texture = 2
            pg.draw.rect(self.surf, slider[1]/1.75, (rect[0], rect[1] + rect[3] / 4, rect[2], rect[3] / 2))
            pg.draw.rect(self.surf, (0, 0, 0), (rect[0], rect[1] + rect[3] / 4, rect[2], rect[3] / 2), 1)
            pg.draw.circle(self.surf, slider[1], (rect[0] + ((self.values[slider[3]] - slider[2][0]) / slider[2][1]) * rect[2], rect[1] + rect[3] / 2), rect[3] / 2)
            pg.draw.circle(self.surf, (0, 0, 0), (rect[0] + ((self.values[slider[3]] - slider[2][0]) / slider[2][1]) * rect[2], rect[1] + rect[3] / 2), rect[3] / 2, 1)

            self.text_handler.render_text(self.surf, (rect[0] + rect[2] + rect[3]/1.5, rect[1] - rect[3] * .15, rect[3] * 1.5, rect[3] * 1.3), f'{float(self.values[slider[3]]):.3}', 'default', 14, (255, 255, 255), (0, 0, 0, 100), True, True)

    def draw_text(self, text_boxes):
        for text_box in text_boxes:
            rect = self.get_rect(text_box)
            self.text_handler.render_text(self.surf, rect, *text_box[2])

    def draw_buttons(self, btns):
        rects = []
        for button in btns:
            rect = self.get_rect(button)
            img = pg.transform.scale(button[1], [*rect[2:]])

            rects.append((rect, *button[-2:]))
            if button[1]: self.surf.blit(img, rect)


        if self.mouse_buttons[0] and not self.mouse_states[0]:
            for button in rects:
                if not button[1]: continue
                if not (button[0][0] < self.mouse_pos[0] < button[0][0] + button[0][2] and button[0][1] < self.mouse_pos[1] < button[0][1] + button[0][3]): continue
                button[1](*button[2])
                self.update_texture = 2

    def main_menu(self):
        self.surf.fill((0, 0, 0, 100))
        self.draw_buttons(self.current_buttons)
        self.draw_sliders(self.current_sliders)
        if self.update_texture > 0: self.draw_text(self.current_text_boxes)

    def hud(self):
        self.surf.fill((255, 0, 0, 0))
        self.draw_buttons(self.current_buttons)
        self.draw_sliders(self.current_sliders)
        if self.update_texture > 0: self.draw_text(self.current_text_boxes)

        card_size = self.win_size[0] / self.n_cards / 2, self.win_size[1] / 5

        for i in range(self.n_cards):
            pg.draw.rect(self.surf, (255, 0, 0, 255), (self.win_size[0] / 2 - (card_size[0] + 5) * self.n_cards/2 + i * (card_size[0] + 5), self.win_size[1] - card_size[1] - 5, card_size[0], card_size[1]))