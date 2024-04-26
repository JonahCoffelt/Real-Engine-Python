import pygame as pg
import numpy as np
import random
import moderngl as mgl
from data.config import config
from data.sheet_spliter import load_sheet
from data.text_handler import TextHandler
from data.ui_screen_data import ScreenData, special_keys, element_indicies, launch_type_indicies, spread_type_indiceis, element_colors
import cudart

assets = {'btn_blank' : 'button_blank.png',
          'btn' : 'button.png'}

class UI_Handler:
    def __init__(self, scene, ctx, frame_vao, win_size=(900, 600)):
        self.scene = scene
        self.ctx = ctx
        self.frame_vao = frame_vao
        self.win_size = win_size
        self.text_handler = TextHandler()

        self.surf = pg.Surface(win_size).convert_alpha()
        self.text_handler = TextHandler()
        self.screen_data = ScreenData(self).screen_data
        self.deck_handler = self.scene.entity_handler.entities[0].deck_handler
        self.sprites = load_sheet()
        self.init_texture()

        self.assets = {asset : pg.image.load(f'UI_Assets/{assets[asset]}').convert_alpha() for asset in assets}
        self.values = {
            'sound' : 0.0,
            'music' : 0.0,
            'FOV' : 90.0,
            'render_distance' : 10,
            'view_distance' : 250,
            'lighting_distance' : 50,
            'selected_card' : 2,
            'health' : 7,
            'max_health' : 10
            }
        self.shop_cards = []
        
        # hud card information
        self.update_card_info()
        self.selected_inv_card = None

        self.mouse_states = [False, False, False]
        self.key_states = pg.key.get_pressed()

        self.screen = self.pause
        self.await_func = [None, None, []]  # event.type, function to call, args
        data = self.screen_data[self.screen]
        self.current_screen_data = {key : value.copy() for key, value in zip(data.keys(), data.values())}

        self.update_texture = 2
        self.scroll = 0

    def update(self):
        # updates card and player information
        self.update_card_info()
        self.update_health_info()
        
        # Handles all keyboard and mouse input for UI
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_buttons = pg.mouse.get_pressed()
        self.keys = pg.key.get_pressed()
        self.update_elements()
        self.mouse_states = [state for state in self.mouse_buttons]
        self.key_states = self.keys

        # Calls the function of the current screen
        if self.update_texture >= 0: self.screen()

        # Used to limit the number of draw calls
        if self.update_texture >= 0: self.update_texture -= 1

        # Renders the Texture
        if self.update_texture == 0 or self.update_texture == 1: self.render()

    def init_texture(self):
        self.tex = self.ctx.texture(self.surf.get_size(), 4)
        self.tex.filter = (mgl.NEAREST, mgl.NEAREST)
        self.tex.swizzel = 'BGRA'

    def surf_to_texture(self):
        self.tex.write(self.surf.get_view('1'))

    def surf_test(self):
        self.surf_to_texture()

    def render(self):
        self.frame_vao.program['UITexture'] = 5
        self.surf_to_texture()
        self.tex.use(location=5)

    def draw(self):
        if not(self.update_texture == 0 or self.update_texture == 1 or self.update_texture == 2): return
        self.execute_draw_calls()
        self.draw_images()
        self.draw_sliders()
        self.draw_text()

    def update_elements(self):
        scroll_bounds = self.current_screen_data['scroll']
        self.scroll = min(max(self.scroll, scroll_bounds[0]), scroll_bounds[1])
        self.update_hotkeys()
        self.update_buttons()
        self.update_sliders()

    def get_events(self, events):
        for event in events:
            if event.type == pg.VIDEORESIZE:
                self.update_texture = 2
                self.win_size = (event.w, event.h)
                self.surf = pg.Surface((event.w, event.h)).convert_alpha()

            if event.type == pg.MOUSEWHEEL:
                self.update_texture = 2
                self.scroll += event.y/10

            if int(event.type) in list(self.current_screen_data['events'].keys()):
                func = self.current_screen_data['events'][int(pg.MOUSEWHEEL)]
                func[0](event, *func[1])

            if event.type == self.await_func[0]:
                self.await_func[1](event, *self.await_func[2])

    def set_attrib(self, category, var, value):
        config[category][var] = value

    def set_await(self, type, func, args: list):
        self.await_func = [type, func, args]

    def await_key(self, event, category, value, key_index):
        if event.key == pg.K_ESCAPE: return

        config[category][value] = event.key
        config[category + '_keys'][value] = event.unicode
        if event.key in special_keys: config[category + '_keys'][value] = special_keys[event.key]
        self.screen_data[self.screen]['text'][key_index][2][0] = config[category + '_keys'][value]
        self.await_func = [None, None, []]
        data = self.screen_data[self.screen]
        self.current_screen_data = {key : value.copy() for key, value in zip(data.keys(), data.values())}
        self.update_texture = 2

    def log(self, txt=''):
        print(txt)
        self.update_texture = 2

    def set_screen(self, screen):
        if screen in [self.main_menu, self.pause, self.shop, self.inventory]:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
        elif screen in [self.hud]:
            pg.event.set_grab(True)
            pg.mouse.set_visible(False) 
        self.update_texture = 2
        self.scroll = 0
        self.screen = screen
        data = self.screen_data[screen]
        self.current_screen_data = {key : value.copy() for key, value in zip(data.keys(), data.values())}
    
    def increment_card(self, event):
        val = self.values['selected_card'] + event.y
        self.values['selected_card'] = min(max(val, 0), self.n_cards-1)

    def set_selected_inv_card(self, card):
        self.selected_inv_card = card

    def move_card(self, card, destination):
        match destination:
            case 'deck':
                self.deck_handler.inventory_to_deck(card)
            case 'inv':
                self.deck_handler.all_to_inventory(card)

    def apply_settings(self):
        self.scene.update_settings()

    def add_button(self, pos: tuple=(.5, .5, .1, .1), img: pg.image=None, func=None, args: list=[], scroll=True):
        if pos == "rndm": pos = np.array([random.uniform(0, 1), random.uniform(0, 1), .1, .1])
        self.current_screen_data['buttons'].append([np.array([*pos]), img, func, [*args], scroll])
    
    def add_draw_call(self, func, pos: tuple=(.5, .5, .1, .1), img: pg.image=None, color=(0, 0, 0, 255), outline=0, scroll=True):
        self.current_screen_data['draw_calls'].append((func, [color, np.array(pos), outline], scroll))

    def add_image(self, img, pos: tuple=(.5, .5, .1, .1), scroll=True):
        self.current_screen_data['images'].append((np.array(pos), img, scroll))

    def get_rect(self, element):
        win_scale = np.array([self.win_size[0], self.win_size[1], self.win_size[0], self.win_size[1]])
        rect = (element[0] * win_scale)
        rect[0] -= rect[2]/2
        rect[1] -= rect[3]/2

        if 0.0 in rect[2:]:
            index = np.where(rect==0.0)[0][0]
            if type(element[1]) == str: img_rect = self.assets[element[1]].get_rect()
            else: img_rect = element[1].get_rect()
            if index == 2:
                rect[2] = rect[3] * (img_rect[2] / img_rect[3])
                rect[0] -= rect[2]/2
            if index == 3:
                rect[3] = rect[2] * (img_rect[3] / img_rect[2])
                rect[1] -= rect[3]/2
        
        if element[-1]: rect[1] += self.scroll * self.win_size[1]

        return rect

    def update_hotkeys(self):
        for key in self.current_screen_data['hotkeys']:
            if self.keys[key] and not self.key_states[key]:
                for command in self.current_screen_data['hotkeys'][key]: command[0](*command[1])

    def update_buttons(self):
        if not(self.mouse_buttons[0] and not self.mouse_states[0]): return
        for button in self.current_screen_data['buttons']:
            rect = self.get_rect(button)
            if not (rect[0] < self.mouse_pos[0] < rect[0] + rect[2] and rect[1] < self.mouse_pos[1] < rect[1] + rect[3]): continue
            button[2](*button[3])
            self.update_texture = 2

    def update_sliders(self):
        if not self.mouse_buttons[0]: return
        for slider in self.current_screen_data['sliders']:
            rect = self.get_rect(slider)
            if self.mouse_buttons[0]:
                if (rect[0] < self.mouse_pos[0] < rect[0] + rect[2] and rect[1] < self.mouse_pos[1] < rect[1] + rect[3]):
                    config[slider[3][0]][slider[3][1]] = min(max(((self.mouse_pos[0] - rect[0] + rect[3]/4) / rect[2]) * (slider[2][1] - slider[2][0]) + slider[2][0], slider[2][0]), slider[2][1])
                    config[slider[3][0]][slider[3][1]] -= config[slider[3][0]][slider[3][1]] % slider[2][2]
                    self.update_texture = 2

    def execute_draw_calls(self):
        for func in self.current_screen_data['draw_calls']:
            rect = self.get_rect([func[1][1], func[-1]])
            func[0](self.surf, func[1][0], rect)

    def draw_sliders(self):
        for slider in self.current_screen_data['sliders']:
            rect = self.get_rect(slider)
            pg.draw.rect(self.surf, slider[1]/1.5, (rect[0], rect[1] + rect[3] / 4, rect[2], rect[3] / 2))
            pg.draw.rect(self.surf, (0, 0, 0), (rect[0], rect[1] + rect[3] / 4, rect[2], rect[3] / 2), 1)
            pg.draw.circle(self.surf, slider[1], (rect[0] + ((config[slider[3][0]][slider[3][1]] - slider[2][0]) / (slider[2][1] - slider[2][0])) * rect[2], rect[1] + rect[3] / 2), rect[3] / 2.5)

            self.text_handler.render_text(self.surf, (rect[0] + rect[2] + rect[3]/1.5, rect[1] - rect[3] * .15, rect[3] * 2, rect[3] * 1.3), f'{float(config[slider[3][0]][slider[3][1]]):.4}', 'default', 14, (255, 255, 255), (0, 0, 0, 100), True, True)

    def draw_text(self):
        for text_box in self.current_screen_data['text']:
            rect = self.get_rect(text_box)
            self.text_handler.render_text(self.surf, rect, *text_box[2])

    def draw_images(self):
        for button in self.current_screen_data['images']:
            rect = self.get_rect(button)
            if type(button[1]) == str: img = self.assets[button[1]]
            else: img = button[1]
            img = pg.transform.scale(img, [*rect[2:]])
            self.surf.blit(img, rect)

    def get_card_surf(self, card_hieght, dist, card):
        element = element_indicies[card.element.name]
        launch = launch_type_indicies[card.launch_type]
        spread = spread_type_indiceis[card.spread_type]
        damage = str(card.damage)
        count = card.count + 11
        force = str(float(card.force))
        radius = str(float(card.radius))
        if len(damage) == 1: damage = '0' + damage
        damage_1, damage_2 = int(damage[0]) + 11, int(damage[1]) + 11
        radius_1, radius_2 = int(radius[0]) + 11, int(radius[2]) + 11
        force_1, force_2 = int(force[0]) + 11, int(force[2]) + 11

        # Get card template of element
        card_surf = self.sprites[element].copy()

        # Blit the numbers on the top
        card_surf.blit(self.sprites[damage_1], (2, 2))
        card_surf.blit(self.sprites[damage_2], (6, 2))
        card_surf.blit(self.sprites[count], (14, 2))

        # Blit the symbols
        card_surf.blit(self.sprites[launch], (6, 12))
        card_surf.blit(self.sprites[spread], (14, 12))

        # Blit radius
        card_surf.blit(self.sprites[radius_1], (11, 19))
        card_surf.blit(self.sprites[21], (14, 19))
        card_surf.blit(self.sprites[radius_2], (17, 19))

        # Blit force
        card_surf.blit(self.sprites[force_1], (11, 25))
        card_surf.blit(self.sprites[21], (14, 25))
        card_surf.blit(self.sprites[force_2], (17, 25))

        scale_constant = (self.n_cards / 2 - (dist - 1)) * .1 + .9
        card_surf = pg.transform.scale(card_surf, (card_hieght * 2/3 * scale_constant , card_hieght * scale_constant))
        return card_surf

    def get_card_preview_surf(self, card, dim):
        preview_surf = pg.Surface((int(9 * dim[0]/dim[1]), 9)).convert()
        color = element_colors[card.element.name]
        preview_surf.fill(color)
        pg.draw.rect(preview_surf, (color[0] * .4, color[1] * .4, color[2] * .4), (0, 0, int(9 * dim[0]/dim[1]), 9), 1)

        damage = str(card.damage)
        if len(damage) == 1: damage = '0' + damage
        damage_1, damage_2 = int(damage[0]) + 11, int(damage[1]) + 11
        count = card.count + 11

        # Blit damage and count
        preview_surf.blit(self.sprites[damage_1], (2, 2))
        preview_surf.blit(self.sprites[damage_2], (6, 2))
        preview_surf.blit(self.sprites[28], (9, 2))
        preview_surf.blit(self.sprites[count], (14, 2))

        preview_surf = pg.transform.scale(preview_surf, dim)

        return preview_surf

    def main_menu(self):
        self.surf.fill((0, 0, 0, 100))
        self.draw()

    def pause(self):
        self.surf.fill((0, 0, 0, 100))
        self.draw()

    def settings_general(self):
        self.surf.fill((0, 0, 0, 100))
        self.draw()

    def settings_control(self):
        self.surf.fill((0, 0, 0, 100))
        self.draw()

    def settings_graphics(self):
        self.surf.fill((0, 0, 0, 100))
        self.draw()

    def inventory(self):
        self.surf.fill((0, 0, 0, 100))

        # Draw side card
        win_scale = np.array([self.win_size[0], self.win_size[1], self.win_size[0], self.win_size[1]])
        card_width = self.win_size[0]/6
        card = self.get_card_surf(card_width * 3/2, 1, self.selected_inv_card)
        rect = np.array([.05, .5, .15, .15 * 3/2])
        rect[1] -= card.get_rect()[3]/2/win_scale[1]
        self.surf.blit(card, (rect[:2] * win_scale[:2]))

        data = self.screen_data[self.screen]
        self.current_screen_data = {key : value.copy() for key, value in zip(data.keys(), data.values())}

        for y, card in enumerate(self.inventory_cards):
            rect = (.5, (y + 3) * .08, .25, .075)
            # Card preview info
            preview = self.get_card_preview_surf(card, (rect[2] * self.win_size[0], rect[3] * self.win_size[1]))
            self.add_image(preview, rect)
            self.add_button((.5, (y + 3) * .08, .25, .075), preview, self.set_selected_inv_card, [card], True)
            # Add card button
            self.add_image(self.sprites[29], (rect[0] + rect[2] / 2 - rect[3]/3, rect[1], rect[3] * .45, rect[3] * .65))
            self.add_button((rect[0] + rect[2] / 2 - rect[3]/3, rect[1], rect[3] * .45, rect[3] * .65), preview, self.move_card, [card, 'deck'], True)
        
        for y, card in enumerate(self.deck):
            rect = (.82, (y + 3) * .08, .25, .075)
            # Card preview info
            preview = self.get_card_preview_surf(card, (rect[2] * self.win_size[0], rect[3] * self.win_size[1]))
            self.add_image(preview, rect)
            self.add_button((.82, (y + 3) * .08, .25, .075), preview, self.set_selected_inv_card, [card], True)
            # Add card button
            self.add_image(self.sprites[30], (rect[0] + rect[2] / 2 - rect[3]/3, rect[1], rect[3] * .45, rect[3] * .65))
            self.add_button((rect[0] + rect[2] / 2 - rect[3]/3, rect[1], rect[3] * .45, rect[3] * .65), preview, self.move_card, [card, 'inv'], True)

        self.draw()
    
    def buy_card(self, index):
        self.shop_cards[index] = False
        self.update_texture = 2

    def shop(self):
        self.surf.fill((0, 0, 0, 100))

        data = self.screen_data[self.screen]
        self.current_screen_data = {key : value.copy() for key, value in zip(data.keys(), data.values())}

        win_scale = np.array([self.win_size[0], self.win_size[1], self.win_size[0], self.win_size[1]])
        card_width = self.win_size[0]/6
        for i in range(3):
            if not self.shop_cards[i]: continue
            card = self.get_card_surf(card_width * 3/2, 1, self.shop_cards[i])
            rect = card.get_rect()
            w = rect[2]
            offset = (self.win_size[0] - (w + 15) * 3 - 15) / 2
            btn_rect = np.array([offset + i * (w + 15), self.win_size[1] - w * 3/2 - .1 * self.win_size[1], rect[2], rect[3]])
            self.surf.blit(card, btn_rect[:2])
            btn_rect /= win_scale
            btn_rect[0] += btn_rect[2]/2
            btn_rect[1] += btn_rect[3]/2 - .1
            self.current_screen_data['buttons'].append((btn_rect, None, self.buy_card, [i], False))
            if self.shop_cards[i]: self.current_screen_data['text'].append((np.array([btn_rect[0], .95, btn_rect[2]/2, .075]), None, (f'${i*2+2}', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False))

        self.draw()

    def hud(self):
        self.surf.fill((0, 0, 0, 0))
        self.draw()

        # Draw the crosshair circle
        pg.draw.circle(self.surf, (0, 0, 0), (self.win_size[0]/2, self.win_size[1]/2), self.win_size[0]/400)

        # Draws the health bar
        win_scale = np.array([self.win_size[0], self.win_size[1], self.win_size[0], self.win_size[1]])
        rect = np.array([.01, .01, .4, .05]) * win_scale
        pg.draw.rect(self.surf, (200, 50, 20, 155), (*rect[:2], rect[2] * (self.values['health'] / self.values['max_health']), rect[3]))
        pg.draw.rect(self.surf, (0, 0, 0, 255), rect, 1)

        # Draws the hand
        card_hieght = self.win_size[1] / 6
        offset = (self.win_size[0] - (len(self.hand) - 1) * (card_hieght * 2/3 + 3)) / 2
        self.values['selected_card'] = max(min(self.values['selected_card'], len(self.hand)-1), 0)
        for i in range(len(self.hand)):
            w, h = card_hieght * 2/3, card_hieght
            index = i - self.values['selected_card']
            dist = abs(index)
            card = self.get_card_surf(card_hieght, dist, self.hand[i])
            card = pg.transform.rotate(card, -np.sqrt(dist) * 10 * np.sign(index))
            self.surf.blit(card, (offset + i * (w + 3) - index * 15 - w/2, self.win_size[1] - h * 1.5 + np.sqrt(dist) * 50))
            
    def update_card_info(self):
        
        self.hand = self.get_player_card_data('hand')
        self.deck = self.get_player_card_data('all')
        self.inventory_cards = self.get_player_card_data('inventory')
        self.n_cards = len(self.hand)

    def update_health_info(self):
        
        self.values['health'] = self.scene.entity_handler.entities[0].health
        self.values['max_health'] = self.scene.entity_handler.entities[0].max_health


    def get_player_card_data(self, data : str):
    
        match data:
            case 'hand': return self.deck_handler.hand
            case 'deck': return self.deck_handler.deck
            case 'inventory': return self.deck_handler.inventory
            case 'all': return self.deck_handler.get_all_cards()
            case _: assert False, 'not a valid card location'