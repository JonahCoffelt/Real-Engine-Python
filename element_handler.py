from dataclasses import dataclass
import random

class ElementHandler():
    
    def __init__(self):
        
        self.elements = {
            'fire' :    Element('fire',     ['water', 'brown'],     (1, 0, 0),          1,      6),
            'water' :   Element('water',    ['electric', 'ice'],    (0, 0, 1),          0,      7),
            'air' :     Element('air',      ['electric', 'psychic'],(0.75, 0.75, 0.75), 0,      8),
            'brown' :   Element('brown',    ['air', 'water', 'ice'],(0.34, 0.16, 0),    -0.5,   9),
            'psychic' : Element('psychic',  ['fire', 'light'],      (1, 0, 1),          1,      10),
            'electric' :Element('electric', ['brown', 'dark'],      (1, 1, 0),          0,      11),
            'acid' :    Element('acid',     ['water', 'brown'],     (0, 1, 0),          1,      12),
            'light' :   Element('light',    ['dark'],               (1, 1, 1),          0,      13),
            'dark' :    Element('dark',     ['light'],              (0, 0, 0),          1,      14),
            'ice' :     Element('ice',      ['fire', 'acid'],       (0.5, 0.5, 1),      -0.5,   15),
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
