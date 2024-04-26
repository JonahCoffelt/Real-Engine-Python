import glm
import random

# returns point of origin and primary direction for spell casting
class CastingHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    def on_init(self):
        ...
        
        
    # cast from casters location to the enemy
    def get_from_self(self, count):
        def from_self(origin, direction):
            return [origin for _ in range(count)], [direction for _ in range(count)]
        return from_self