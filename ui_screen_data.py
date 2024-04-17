import numpy as np
import pygame as pg

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

launch_type_indicies = {
    'lob' : 22, 
    'straight' : 23, 
    'confused' : 24
}

spread_type_indiceis = {
    'vertical' : 25, 
    'horizontal' : 26
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
                    (np.array([.5, .2,  .6, .2]), None, ('Dicey Decks', 'default', 60, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .4,  .4, .1]), None, ('Start', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .55, .4, .1]), None, ('Settings', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .7,  .4, .1]), None, ('Quit', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False)
                ],
                'buttons' : [
                    (np.array([.5, .4,  .6, .1]), None, UI.set_screen, [UI.hud], False),
                    (np.array([.5, .55, .6, .1]), None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.5, .7,  .6, .1]), None, UI.log, ["quit"], False)
                ],
                'sliders' : [],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.hud]], [UI.log, ["Switching screen to HUD"]]],
                    pg.K_e : [[UI.log, ['Pressed "E"']]]
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
                    pg.K_e : [[UI.set_screen, [UI.inventory]]],
                    pg.K_q : [[UI.set_screen, [UI.shop]]]
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
                    (np.array([.5, .4,  .6, .1]), None, ('Resume', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .55, .6, .1]), None, ('Settings', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.5, .7,  .6, .1]), None, ('Exit', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False)
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
                    (np.array([.15, .2,  .275, .1]),    None, ('General', 'default', 20, (220, 220, 220), (200, 200, 200, 100), True, True), False),
                    (np.array([.15, .32,  .275, .1]),   None, ('Controls', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .44,  .275, .1]),   None, ('Graphics', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .86,  .275, .075]), None, ('Back', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.9, .86,  .175, .075]),  None, ('Apply', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                    (np.array([.425, .175, .2, .05]),    None, ('Volume', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .25, .2, .05]),    None, ('Sound', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .325, .2, .05]),    None, ('Music', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                ],
                'buttons' : [
                    (np.array([.15, .2,  .275, .1]),    None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.15, .32,  .275, .1]),   None, UI.set_screen, [UI.settings_control], False),
                    (np.array([.15, .44,  .275, .1]),   None, UI.set_screen, [UI.settings_graphics], False),
                    (np.array([.15, .86,  .275, .075]), None, UI.set_screen, [UI.pause], False),
                    (np.array([.9, .86,  .175, .075]),  None, UI.log, ['Apply Settings'], False)
                ],
                'sliders' : [
                    (np.array([.75, .25, .3, .05]), np.array([50, 150, 255]), (0, 100, 5), 'sound', False),
                    (np.array([.75, .325, .3, .05]), np.array([50, 150, 255]), (0, 100, 5), 'music', False)
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
                    (np.array([.15, .2,  .275, .1]),    None, ('General', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .32,  .275, .1]),   None, ('Controls', 'default', 20, (220, 220, 220), (200, 200, 200, 100), True, True), False),
                    (np.array([.15, .44,  .275, .1]),   None, ('Graphics', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .86,  .275, .075]), None, ('Back', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.9, .86,  .175, .075]),  None, ('Apply', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                    (np.array([.425, .175, .2, .05]),   None, ('Forward', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .175, .2, .05]),   None, ['_', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .25, .2, .05]),   None, ('Backward', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .25, .2, .05]),   None, ['_', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .325, .2, .05]),   None, ('Left', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .325, .2, .05]),   None, ['_', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .4, .2, .05]),   None, ('Right', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .4, .2, .05]),   None, ['_', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .475, .2, .05]),   None, ('Jump', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .475, .2, .05]),   None, ['_', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],

                    (np.array([.425, .55, .2, .05]),   None, ('Interact', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), True),
                    [np.array([.65, .55, .2, .05]),   None, ['_', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True], True],
                ],
                'buttons' : [
                    (np.array([.15, .2,  .275, .1]),    None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.15, .32,  .275, .1]),   None, UI.set_screen, [UI.settings_control], False),
                    (np.array([.15, .44,  .275, .1]),   None, UI.set_screen, [UI.settings_graphics], False),
                    (np.array([.15, .86,  .275, .075]), None, UI.set_screen, [UI.pause], False),
                    (np.array([.9, .86,  .175, .075]),  None, UI.log, ['Apply Settings'], False),

                    (np.array([.65, .175, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'forward', 6]], True),
                    (np.array([.65, .25, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'backward', 8]], True),
                    (np.array([.65, .325, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'left', 10]], True),
                    (np.array([.65, .4, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'right', 12]], True),
                    (np.array([.65, .475, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'jump', 14]], True),
                    (np.array([.65, .55, .2, .05]),  None, UI.set_await, [pg.KEYDOWN, UI.await_key, ['controls', 'interact', 16]], True)
                ],
                'sliders' : [],
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
                    (np.array([.15, .2,  .275, .1]),    None, ('General', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .32,  .275, .1]),   None, ('Controls', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.15, .44,  .275, .1]),   None, ('Graphics', 'default', 20, (220, 220, 220), (200, 200, 200, 100), True, True), False),
                    (np.array([.15, .86,  .275, .075]), None, ('Back', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.9, .86,  .175, .075]),  None, ('Apply', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),

                    (np.array([.425, .175, .2, .05]),   None, ('FOV', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .25, .2, .05]),   None, ('Chunk Distance', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .325, .2, .05]),   None, ('View Distance', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                    (np.array([.425, .4, .2, .05]),   None, ('Light Distance', 'default', 16, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                ],
                'buttons' : [
                    (np.array([.15, .2,  .275, .1]),    None, UI.set_screen, [UI.settings_general], False),
                    (np.array([.15, .32,  .275, .1]),   None, UI.set_screen, [UI.settings_control], False),
                    (np.array([.15, .44,  .275, .1]),   None, UI.set_screen, [UI.settings_graphics], False),
                    (np.array([.15, .86,  .275, .075]), None, UI.set_screen, [UI.pause], False),
                    (np.array([.9, .86,  .175, .075]),  None, UI.log, ['Apply Settings'], False),
                ],
                'sliders' : [
                    (np.array([.75, .175, .3, .05]), np.array([50, 150, 255]), (50, 120, 5), 'FOV', False),
                    (np.array([.75, .25, .3, .05]), np.array([50, 150, 255]), (2, 20, 2), 'render_distance', False),
                    (np.array([.75, .325, .3, .05]), np.array([50, 150, 255]), (100, 400, 10), 'view_distance', False),
                    (np.array([.75, .4, .3, .05]), np.array([50, 150, 255]), (10, 100, 5), 'lighting_distance', False)
                ],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.pause]]]
                },
                'events' : {}
            },

            UI.inventory : {
                'scroll' : [0, 0],
                'images' : [
                    
                ],
                'draw_calls' : [
                    (pg.draw.rect, [(0, 255, 0, 200), np.array([0.33, 0.55, 0.005, 0.7])], False),
                    (pg.draw.rect, [(0, 0, 0, 200), np.array([0.66, 0.55, 0.005, 0.7])], False)
                ],
                'text' : [
                    (np.array([.5, .075,  .3, .1]), None, ('Inventory', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                ],
                'buttons' : [
                ],
                'sliders' : [],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.hud]]]
                },
                'events' : {}
            },

            UI.shop : {
                'scroll' : [0, 0],
                'images' : [
                    
                ],
                'draw_calls' : [],
                'text' : [
                    (np.array([.5, .075,  .3, .1]), None, ('Shop', 'default', 20, (220, 220, 220), (0, 0, 0, 100), True, True), False),
                ],
                'buttons' : [
                ],
                'sliders' : [],
                'hotkeys' : {
                    pg.K_ESCAPE : [[UI.set_screen, [UI.hud]]]
                },
                'events' : {}
            },
        }