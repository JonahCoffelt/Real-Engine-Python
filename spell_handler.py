import numpy as np

class SpellHandler():
    
    def __init__(self):
        
        self.spells = []
        self.launch_handler = LaunchHandler()
        self.spread_handler = SpreadHandler()
        
        self.on_init()
        
    def on_init(self): 
        
        ...
    
class LaunchHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    # functions
    def get_straight(self, direction, speed):
        
        def straight(pos):
            return pos + direction * speed
            
        return straight
        
    def get_lob(self, direction, speed, gravity):
        
        ...
        
class SpreadHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    # functions - return list of directions
    def get_horizontal(self, count, angle):
        
        ...
        
    def get_vertical(self, count, angle):
        
        ...
    
class Spell():
    
    def __init__(self, spell_handler : SpellHandler, damage, radius, speed, spread_type = 'horizontal', launch_type = 'straight', count = 1, angle = np.pi/3, destructive = False):
        
        # spell handler to make programs
        self.spell_handler = spell_handler
        
        # spell stats 
        self.damage = damage
        self.radius = radius
        self.destructive = destructive
        
        # gets spread program
        match spread_type:
            case 'horizontal': self.spread_program = self.spell_handler.spread_handler.get_horizontal(count, angle)
            case 'vertical': self.spread_program = self.spell_handler.spread_handler.get_vertical(count, angle)
            case _: assert False, 'spread program does not exist'
        
    def get_bullets(self, pos, direction):
        
        ...
        
class Bullet():
    
    def __init__(self, pos, launch_program):
        
        self.pos = pos
        self.launch_program = launch_program
        
    def move(self):
        
        self.pos = self.launch_program(self.pos)