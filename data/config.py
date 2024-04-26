import pygame as pg

config = {
    'runtime' : {
        'simulate' : False,
        'render' : True,
        'level' : 'hub'
    },
    'controls' : {
        'forward' : pg.K_w,
        'backward' : pg.K_s,
        'left' : pg.K_a,
        'right' : pg.K_d,
        'roll' : pg.K_SPACE,
        'up' : pg.K_SPACE,
        'down' : pg.K_LSHIFT,
        'inventory' : pg.K_e,
        'sensitivity' : 1.5
    },
    'controls_keys' : {
        'forward' : 'w',
        'backward' : 's',
        'left' : 'a',
        'right' : 'd',
        'roll' : 'Space',
        'up' : 'Space',
        'down' : 'Shift',
        'inventory' : 'e',
    },
    'menu_controls' : {
        'menu' : [pg.K_ESCAPE],
        'select' : [pg.K_RETURN],
        'up' : [pg.K_w, pg.K_UP],
        'dowm' : [pg.K_s, pg.K_DOWN],
        'right' : [pg.K_d, pg.K_RIGHT],
        'left' : [pg.K_a, pg.K_LEFT],
    },
    'settings' : {
        'sound' : 25.0,
        'music' : 25.0
    },
    'graphics' : {
        'FOV' : 75.0,
        'aspect_ratio' : 16/9,
        'render_distance' : 10,
        'far_plane_distance' : 250,
        'light_range' : 50,
        'particle_range' : 50,
        'full_screen' : False
    },
    'simulation' : {
        'simulation_distance' : 5,
    }
}