import numpy as np
import random
from object_handler import Object
from model import BaseModel

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
                #'vertical' : 0,
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
        spread_type = random.choice(['horizontal'])
        damage = random.randint(1, 10)
        radius = random.uniform(0.1, 3.0)
        speed = random.uniform(5, 20)
        force = random.uniform(0.1, 3)
        count = random.randint(1, 7)
        angle = random.uniform(np.pi/3, np.pi)
        
        return Spell(self, damage, radius, speed, force, spread_type, launch_type, count, angle, True)
    
    def update(self, delta_time):
        self.bullet_handler.update(delta_time)
    
class LaunchHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    # functions
    def get_straight(self, direction, speed):
        
        def program(pos, delta_time):
            return pos + direction * speed * delta_time
            
        return program
        
    def get_lob(self, direction, speed, gravity):
        
        def program(pos, delta_time):
            pos = pos + direction * speed * delta_time
            pos[1] -= gravity
            return pos
            
        return program
        
class SpreadHandler():
    
    def __init__(self):
            
        self.programs = {}
        self.on_init()
    
    def on_init(self):
        
        # speard program for single shot
        def single(direction):
            return [direction]
        self.programs['single'] = single
        
    # functions - return list of directions
    def get_horizontal(self, count, angle):
        
        angles = self.get_angles(count, angle)
        rot_mats = [self.get_xz_rot_mat(a) for a in angles]
        
        def program(direction):
            return [np.array([float(i) for i in mat * direction.reshape((3, 1))]) for mat in rot_mats]
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
        return np.matrix([[np.cos(angle), -np.sin(angle), 0], 
                         [np.sin(angle), 0, np.cos(angle)], 
                         [0, 0, 1]])
    
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
    def get_bullets(self, pos, direction : np.array):
        
        # gets all directions of bullets fired
        directions = self.spread_program(direction)
        
        # returns a list of bullets using launch program
        match self.launch_type:
            case 'straight': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self.spell_handler.bullet_handler, pos, self.spell_handler.launch_handler.get_straight(direction, self.speed))) for direction in directions]
            case 'lob': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self.spell_handler.bullet_handler, pos, self.spell_handler.launch_handler.get_lob(direction, self.speed, -9.8))) for direction in directions]
            case _: assert False, 'launch program does not exist'
            
class BulletHandler():
    
    def __init__(self, object_handler):
        
        self.object_handler = object_handler
        self.bullets = []
        
    def update(self, delta_time):
        
        for bullet in self.bullets:
            bullet.move(delta_time)
        
    def add_bullet(self, bullet):
        self.bullets.append(bullet)
        return bullet
        
class Bullet():
    
    def __init__(self, bullet_handler : BulletHandler, pos, launch_program):
        
        self.launch_program = launch_program
        self.bullet_handler = bullet_handler
        self.obj = self.bullet_handler.object_handler.add_object(Object(self.bullet_handler.object_handler, self.bullet_handler.object_handler.scene, BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos = pos, rot = (0, 0, 0), scale=(.2, .2, .2), gravity = False, immovable = True))
        
    def move(self, delta_time):
        
        # checks if bullet has collided
        if self.obj.last_collided is not None:
            self.remove_self()
            return
        
        self.obj.set_pos(self.launch_program(self.obj.pos, delta_time))
        
    def remove_self(self):
        
        # removes from handler lists
        self.bullet_handler.bullets.remove(self)
        self.bullet_handler.object_handler.objects.remove(self.obj)
        
        # delete self from system
        del self.obj
        del self