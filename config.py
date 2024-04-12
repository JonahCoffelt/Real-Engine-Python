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
        'up' : pg.K_SPACE,
        'down' : pg.K_LSHIFT,
        'inventory' : pg.K_e,
        'sensitivity' : 1.5
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
        'volume' : 25.0
    },
    'graphics' : {
        'FOV' : 90.0,
        'aspect_ratio' : 16/9,
        'render_distance' : 10,
        'far_plane_distance' : 250,
        'full_screen' : False
    }
}