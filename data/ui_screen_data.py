import numpy as np
import pygame as pg
import sys
from data.config import config

special_keys = {
    pg.K_UP : 'Up',
    pg.K_DOWN : 'Down',
    pg.K_LEFT : 'Left',
    pg.K_RIGHT : 'Right',
    pg.K_SPACE : 'Space',
    pg.K_RETURN : 'Return',
    pg.K_LSHIFT : 'Shift',
    pg.K_LCTRL : 'Control',
    pg.K_LALT : 'Alt',
    pg.K_CAPSLOCK : 'Capslock',
    pg.K_TAB : 'Tab',
}

element_indicies = {
    'fire' : 1, 
    'water' : 2, 
    'air' : 3, 
    'brown' : 4, 
    'psychic' : 5, 
    'electric' : 6, 
    'acid' : 7, 
    'light' : 8, 
    'dark' : 9, 
    'ice' : 10, 
}

element_colors = {
    'fire' : (165, 48, 48), 
    'water' : (79, 143, 186), 
    'air' : (199, 207, 204), 
    'brown' : (122, 72, 65), 
    'psychic' : (198, 81, 151), 
    'electric' : (232, 193, 112), 
    'acid' : (70, 130, 50), 
    'light' : (231, 213, 179), 
    'dark' : (46, 62, 69), 
    'ice' : (115, 190, 211), 
}

launch_type_indicies = {
    'lob' : 22, 
    'straight' : 23, 
    'confused' : 24
}

spread_type_indiceis = {
    'vertical' : 25, 
    'horizontal' : 26,
    'single' : 27
}

class ScreenData:
    def __init__(self, UI):
        self.screen_data = {
            UI.main_menu : {
                'scroll' : [0, 0],
                'images' : [

                ],
                'draw_calls' : [

                ],
                'text' : [
                    (np.array([.5, .2,  .6, .2]), None, ('Dicey Decks', 'pixel', 60, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .4,  .4, .1]), None, ('Start', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .55,  .4, .1]), None, ('Quit', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False)
                ],
                'buttons' : [
                    (np.array([.5, .4,  .6, .1]), None, UI.set_screen, [UI.hud], False),
                    (np.array([.5, .4,  .6, .1]), None, UI.set_attrib, ['runtime', 'simulate', True], False),
                    (np.array([.5, .55,  .6, .1]), None, sys.exit, [], False)
                ],
                'sliders' : [],
                'hotkeys' : {
                },
                'events' : {}
            },

            UI.hud : {
                'scroll' : [0, 0],
                'images' : [

                ],
                'draw_calls' : [

                ],
                'text' : [
                    
                ],
                'buttons' : [
                    
                ],
                'sliders' : [
                    
                ],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.pause]], [UI.set_attrib, ['runtime', 'simulate', False]]],
                    config['controls']['inventory'] : [[UI.set_screen, [UI.inventory]], [UI.set_attrib, ['runtime', 'simulate', False]]],
                    pg.K_q : [[UI.set_screen, [UI.shop]], [UI.set_attrib, ['runtime', 'simulate', False]]]
                },
                'events' : {
                    pg.MOUSEWHEEL : [UI.increment_card, []]
                }
            },

            UI.pause : {
                'scroll' : [0, 1],
                'images' : [
                    
                ],
                'draw_calls' : [],
                'text' : [
                    (np.array([.5, .4,  .6, .1]), None, ('Resume', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .55, .6, .1]), None, ('Settings', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .7,  .6, .1]), None, ('Exit', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False)
                ],
                'buttons' : [
                    (np.array([.5, .4,  .6, .1]), None, UI.set_attrib, ['runtime', 'simulate', True], False),
                    (np.array([.5, .4,  .6, .1]), None, UI.set_screen, [UI.hud], False),
                    (np.array([.5, .55, .6, .1]), None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.5, .7,  .6, .1]), None, UI.set_screen, [UI.main_menu], False)
                ],
                'sliders' : [],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.hud]], [UI.set_attrib, ['runtime', 'simulate', True]]]
                },
                'events' : {}
            },

            UI.settings_general : {
                'scroll' : [0, 0],
                'images' : [

                ],
                'draw_calls' : [
                    (pg.draw.rect, [(0, 0, 0, 200), np.array([0.3, 0.5, 0.005, 0.8])], False)
                ],
                'text' : [
                    (np.array([.15, .2,  .275, .1]),    None, ('General', 'pixel', 20, (220, 220, 220), (200, 200, 200, 100), True, True), False),
                    (np.array([.15, .32,  .275, .1]),   None, ('Controls', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .44,  .275, .1]),   None, ('Graphics', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .86,  .275, .075]), None, ('Back', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.9, .86,  .175, .075]),  None, ('Apply', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                    (np.array([.425, .175, .2, .05]),    None, ('Volume', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .25, .2, .05]),    None, ('Sound', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .325, .2, .05]),    None, ('Music', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                ],
                'buttons' : [
                    (np.array([.15, .2,  .275, .1]),    None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.15, .32,  .275, .1]),   None, UI.set_screen, [UI.settings_control], False),
                    (np.array([.15, .44,  .275, .1]),   None, UI.set_screen, [UI.settings_graphics], False),
                    (np.array([.15, .86,  .275, .075]), None, UI.set_screen, [UI.pause], False),
                    (np.array([.9, .86,  .175, .075]),  None, UI.apply_settings, [], False)
                ],
                'sliders' : [
                    (np.array([.75, .25, .3, .05]), np.array([50, 150, 255]), (0, 100, 5), ['settings', 'sound'], False),
                    (np.array([.75, .325, .3, .05]), np.array([50, 150, 255]), (0, 100, 5), ['settings', 'music'], False)
                ],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.pause]]]
                },
                'events' : {}
            },

            UI.settings_control : {
                'scroll' : [-.5, 0],
                'images' : [

                ],
                'draw_calls' : [
                    (pg.draw.rect, [(0, 0, 0, 200), np.array([0.3, 0.5, 0.005, 0.8])], False)
                ],
                'text' : [
                    (np.array([.15, .2,  .275, .1]),    None, ('General', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .32,  .275, .1]),   None, ('Controls', 'pixel', 20, (220, 220, 220), (200, 200, 200, 100), True, True), False),
                    (np.array([.15, .44,  .275, .1]),   None, ('Graphics', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .86,  .275, .075]), None, ('Back', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.9, .86,  .175, .075]),  None, ('Apply', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                    (np.array([.425, .175, .2, .05]),   None, ('Sensitivity', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),

                    (np.array([.425, .25, .2, .05]),   None, ('Forward', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .25, .2, .05]),   None, [config['controls_keys']['forward'], 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .325, .2, .05]),   None, ('Backward', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .325, .2, .05]),   None, [config['controls_keys']['backward'], 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .4, .2, .05]),   None, ('Left', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .4, .2, .05]),   None, [config['controls_keys']['left'], 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .475, .2, .05]),   None, ('Right', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .475, .2, .05]),   None, [config['controls_keys']['right'], 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .55, .2, .05]),   None, ('Roll', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .55, .2, .05]),   None, [config['controls_keys']['roll'], 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .625, .2, .05]),   None, ('Inventory', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .625, .2, .05]),   None, [config['controls_keys']['inventory'], 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],
                ],
                'buttons' : [
                    (np.array([.15, .2,  .275, .1]),    None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.15, .32,  .275, .1]),   None, UI.set_screen, [UI.settings_control], False),
                    (np.array([.15, .44,  .275, .1]),   None, UI.set_screen, [UI.settings_graphics], False),
                    (np.array([.15, .86,  .275, .075]), None, UI.set_screen, [UI.pause], False),
                    (np.array([.9, .86,  .175, .075]),  None, UI.apply_settings, [], False),

                    (np.array([.65, .25, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'forward', 7]], True),
                    (np.array([.65, .325, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'backward', 9]], True),
                    (np.array([.65, .4, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'left', 11]], True),
                    (np.array([.65, .475, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'right', 13]], True),
                    (np.array([.65, .55, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'roll', 15]], True),
                    (np.array([.65, .625, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'inventory', 17]], True)
                ],
                'sliders' : [(np.array([.75, .175, .3, .05]), np.array([50, 150, 255]), (.2, 3.0, .1), ['controls', 'sensitivity'], False),],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.pause]]]
                },
                'events' : {}
            },

            UI.settings_graphics : {
                'scroll' : [-1, 1],
                'images' : [

                ],
                'draw_calls' : [
                    (pg.draw.rect, [(0, 0, 0, 200), np.array([0.3, 0.5, 0.005, 0.8])], False)
                ],
                'text' : [
                    (np.array([.15, .2,  .275, .1]),    None, ('General', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .32,  .275, .1]),   None, ('Controls', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .44,  .275, .1]),   None, ('Graphics', 'pixel', 20, (220, 220, 220), (200, 200, 200, 100), True, True), False),
                    (np.array([.15, .86,  .275, .075]), None, ('Back', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.9, .86,  .175, .075]),  None, ('Apply', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                    (np.array([.425, .175, .2, .05]),   None, ('FOV', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .25, .2, .05]),   None, ('Chunk Distance', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .325, .2, .05]),   None, ('View Distance', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .4, .2, .05]),   None, ('Light Distance', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .475, .2, .05]),   None, ('Particle Distance', 'pixel', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                ],
                'buttons' : [
                    (np.array([.15, .2,  .275, .1]),    None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.15, .32,  .275, .1]),   None, UI.set_screen, [UI.settings_control], False),
                    (np.array([.15, .44,  .275, .1]),   None, UI.set_screen, [UI.settings_graphics], False),
                    (np.array([.15, .86,  .275, .075]), None, UI.set_screen, [UI.pause], False),
                    (np.array([.9, .86,  .175, .075]),  None, UI.apply_settings, [], False),
                ],
                'sliders' : [
                    (np.array([.75, .175, .3, .05]), np.array([50, 150, 255]), (50, 120, 5), ['graphics', 'FOV'], False),
                    (np.array([.75, .25, .3, .05]), np.array([50, 150, 255]), (2, 20, 2), ['graphics', 'render_distance'], False),
                    (np.array([.75, .325, .3, .05]), np.array([50, 150, 255]), (100, 400, 10), ['graphics', 'far_plane_distance'], False),
                    (np.array([.75, .4, .3, .05]), np.array([50, 150, 255]), (10, 100, 5), ['graphics', 'light_range'], False),
                    (np.array([.75, .475, .3, .05]), np.array([50, 150, 255]), (10, 100, 5), ['graphics', 'particle_range'], False),
                ],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.pause]]]
                },
                'events' : {}
            },

            UI.inventory : {
                'scroll' : [-1, 0],
                'images' : [
                    
                ],
                'draw_calls' : [
                    (pg.draw.rect, [(0, 0, 0, 200), np.array([0.66, 0.55, 0.005, 0.7])], False)
                ],
                'text' : [
                    (np.array([.5, .075,  .3, .075]), None, ('Inventory', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.82, .075,  .3, .075]), None, ('Deck', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                ],
                'buttons' : [
                ],
                'sliders' : [],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.hud]], [UI.set_attrib, ['runtime', 'simulate', True]]],
                    config['controls']['inventory'] : [[UI.set_screen, [UI.hud]], [UI.set_attrib, ['runtime', 'simulate', True]]]
                },
                'events' : {}
            },

            UI.shop : {
                'scroll' : [0, 0],
                'images' : [
                    
                ],
                'draw_calls' : [],
                'text' : [
                    (np.array([.5, .075,  .3, .1]), None, ('Shop', 'pixel', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                ],
                'buttons' : [
                ],
                'sliders' : [],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.hud]], [UI.set_attrib, ['runtime', 'simulate', True]]],
                },
                'events' : {}
            },
        }