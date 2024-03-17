import numpy as np

class SpellHandler():
    
    def __init__(self):
        
        # spell program handlers
        self.launch_handler = LaunchHandler()
        self.spread_handler = SpreadHandler()
        
        # saved spells list
        self.spells = []
        
        # spell attribute costs, may need to be modified for balance
        self.spell_attributes = {
            'launch_type' : {
                'lob' : 0,
                'straight' : 1
            },
            'spread_type' : {
                'vertical' : 0,
                'horizontal' : 1
            }
        }
        
        """
        Scalar attribute costs
        
        Damage: 1 point per damage
        Radius: points = radius cubed
        Speed: 0.25 points per m/s
        Force: 3 points per m/s of implied velocity
        
        Count: multiply all other scalar attribute costs by count
        Angle: no point change, max = 90 degrees or pi/2
        """
        
    def create_random_spell(self, cost):
        
        ...
    
class LaunchHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    # functions
    def get_straight(self, direction, speed):
        
        def program(pos):
            return pos + direction * speed
            
        return program
        
    def get_lob(self, direction, speed, gravity):
        
        ...
        
class SpreadHandler():
    
    def __init__(self):
            
        self.programs = {}
    
    def on_init(self):
        
        # speard program for single shot
        def single(direction):
            return direction
        self.programs['single'] = single
        
    # functions - return list of directions
    def get_horizontal(self, count, angle):
        
        angles = self.get_angles(count, angle)
        rot_mats = [self.get_xz_rot_mat(a) for a in angles]
        
        def program(direction):
            return [mat * direction for mat in rot_mats]
        return program
        
    def get_vertical(self, count, angle):
        ...
        
    # returns a list of angles to rotate a directional vector
    def get_angles(self, count, angle):
        step, a = 2 / (count - 1), angle/2
        return [(-1 + i * step) * a for i in range(count)]
        
    def get_xz_rot_mat(self, angle):
        return np.matrix([[np.cos(angle), 0, np.sin(angle)], 
                         [0, 1, 0],
                         [-np.sin(angle), 0, np.cos(angle)]])
        
    def get_xy_rot_mat(self, angle):
        ...
    
class Spell():
    
    def __init__(self, spell_handler : SpellHandler, damage, radius, speed, force = 0, spread_type = 'horizontal', launch_type = 'straight', count = 1, angle = np.pi/3, destructive = False):
        
        # spell handler to make programs
        self.spell_handler = spell_handler
        
        # spell stats 
        self.damage = damage
        self.radius = radius
        self.destructive = destructive
        self.force = force
        
        # launch program variables
        self.launch_type = launch_type
        self.speed = speed
        
        # gets spread program
        if count == 1: self.spread_program = self.spell_handler.spread_handler.programs['single']
        else:
            match spread_type:
                case 'horizontal': self.spread_program = self.spell_handler.spread_handler.get_horizontal(count, angle)
                case 'vertical': self.spread_program = self.spell_handler.spread_handler.get_vertical(count, angle)
                case _: assert False, 'spread program does not exist'
        
    # returns a list of bullets from the spell
    def get_bullets(self, pos, direction):
        
        # gets all directions of bullets fired
        directions = self.spread_program(direction)
        
        # returns a list of bullets using launch program
        match self.launch_type:
            case 'straight': return [Bullet(pos, self.spell_handler.launch_handler.get_straight(direction, self.speed)) for direction in directions]
            case 'lob': return [Bullet(pos, self.spell_handler.launch_handler.get_lob(direction, self.speed, -9.8)) for direction in directions]
            case _: assert False, 'launch program does not exist'
        
class Bullet():
    
    def __init__(self, pos, launch_program):
        
        self.pos = pos
        self.launch_program = launch_program
        
    def move(self):
        
        self.pos = self.launch_program(self.pos)