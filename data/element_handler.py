from dataclasses import dataclass
import random


enemy_colors = {
    'default' :  (1.0, 1.0, 1.0),
    'fire' :     (1.0, 0.4, 0.4),
    'water' :    (0.4, 0.4, 1.0),
    'air' :      (1.0, 1.0, 1.0),
    'brown' :    (0.5, 0.5, 0.2),
    'psychic' :  (1.0, 0.2, 1.0),
    'electric' : (1.0, 1.0, 0.0),
    'acid' :     (0.4, 1.0, 0.4),
    'light' :    (1.0, 1.0, 0.5),
    'dark' :     (0.2, 0.2, 0.2),
    'ice' :      (0.6, 0.8, 1.0),
}


class ElementHandler():
    
    def __init__(self):
        
        self.elements = {
            'fire' :    Element('fire',     ['water', 'brown'],     ((.8, .3, .1), (1, .7, .3)),          1,      6),
            'water' :   Element('water',    ['electric', 'ice'],    ((.1, .3, .7), (.2, .5, 1)),          0,      7),
            'air' :     Element('air',      ['electric', 'psychic'],((0.7, 0.7, 0.7), (0.8, 0.8, 0.8)), 0,      8),
            'brown' :   Element('brown',    ['air', 'water', 'ice'],((0.25, 0.1, 0), (0.4, 0.2, 0.1)),    -0.5,   9),
            'psychic' : Element('psychic',  ['fire', 'light'],      ((.7, .1, .7), (.95, .2, .95)),          1,      10),
            'electric' :Element('electric', ['brown', 'dark'],      ((.8, .8, .1), (1, 1, .3)),          0,      11),
            'acid' :    Element('acid',     ['water', 'brown'],     ((0, .5, 0), (.1, .8, .1)),          1,      12),
            'light' :   Element('light',    ['dark'],               ((.8, .8, .7), (1, 1, .9)),          0,      13),
            'dark' :    Element('dark',     ['light'],              ((0.1, 0, 0.1), (0.1, 0.05, 0.15)),          1,      14),
            'ice' :     Element('ice',      ['fire', 'acid'],       ((.4, .6, .8), (.5, .8, 1)),      -0.5,   15),
        }
        
    def get_random_element(self):
        
        return random.choice(list(self.elements.values()))
    
class Element():
    
    def __init__(self, name, weak_to, color, terrain, terrain_material):
        self.name = name
        self.weak_to = weak_to
        self.color = color
        self.terrain = terrain
        self.terrain_material = terrain_material
