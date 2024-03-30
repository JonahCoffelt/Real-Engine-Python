import numpy as np
import random
from bullet_handler import Bullet, BulletHandler
from launch_handler import LaunchHandler
from spread_handler import SpreadHandler

class SpellHandler():
    
    def __init__(self, object_handler):
        
        # spell program handlers
        self.launch_handler = LaunchHandler()
        self.spread_handler = SpreadHandler()
        
        self.object_handler = object_handler
        self.bullet_handler = BulletHandler(self.object_handler)
        
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
        
    def create_random_spell(self):
        
        launch_type = random.choice(['straight'])
        spread_type = random.choice(['horizontal'])#, 'vertical'])
        damage = random.randint(1, 10)
        radius = random.uniform(0, 3.0)
        speed = random.uniform(5, 20)
        force = random.uniform(1, 20)
        count = random.randint(1, 7)
        angle = random.uniform(np.pi/24, np.pi/3)
        color = [random.uniform(0.5, 1) for _ in range(3)]
        
        return Spell(self, damage, radius, speed, force, spread_type, launch_type, count, angle, True, color)
    
    def update(self, delta_time):
        self.bullet_handler.update(delta_time)
    
class Spell():
    
    def __init__(self, spell_handler : SpellHandler, damage, radius, speed, force = 0, spread_type = 'horizontal', launch_type = 'straight', count = 1, angle = np.pi/3, destructive = False, color = (1.0, 1.0, 1.0)):
        
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
        
        # visual variables
        self.color = color
        
        # gets spread program
        if count == 1: self.spread_program = self.spell_handler.spread_handler.programs['single']
        else:
            match spread_type:
                case 'horizontal': self.spread_program = self.spell_handler.spread_handler.get_horizontal(count, angle)
                case 'vertical': self.spread_program = self.spell_handler.spread_handler.get_vertical(count, angle)
                case _: assert False, 'spread program does not exist'
        
    # returns a list of bullets from the spell
    def get_bullets(self, pos, direction : np.array):
        
        # gets all directions of bullets fired
        directions = self.spread_program(direction)
        
        # returns a list of bullets using launch program
        match self.launch_type:
            case 'straight': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self, self.spell_handler.bullet_handler, pos, self.spell_handler.launch_handler.get_straight(direction, self.speed))) for direction in directions]
            case 'lob': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self, self.spell_handler.bullet_handler, pos, self.spell_handler.launch_handler.get_lob(direction, self.speed, -9.8))) for direction in directions]
            case _: assert False, 'launch program does not exist'
            