import numpy as np
import random
from bullet_handler import Bullet, BulletHandler
from launch_handler import LaunchHandler
from spread_handler import SpreadHandler
from casting_handler import CastingHandler
from element_handler import ElementHandler
import cudart


class SpellHandler():
    
    def __init__(self, object_handler):
        
        # spell program handlers
        self.launch_handler = LaunchHandler()
        self.spread_handler = SpreadHandler()
        self.casting_handler = CastingHandler()
        self.element_handler = ElementHandler()
        
        self.object_handler = object_handler
        self.bullet_handler = BulletHandler(self.object_handler)
        
        # saved spells list
        self.spells = []
        
        # spell attribute costs, may need to be modified for balance
        self.spell_attributes = {
            'launch_type' : {
                'lob' : 0,
                'straight' : 1,
                'confused' : 2
            },
            'spread_type' : {
                'vertical' : 0,
                'horizontal' : 1
            },
            'casting_type' : {
                'from_self': 0
            },
            'damage' : 1,
            'radius' : 1, # cubed after
            'speed' : 0.25,
            'force' : 3, # squared after
            
            'angle' : 0,
            'count' : 0 # multiply entire cost after
        }
        
    def create_spell(self, power = 15, element = None):
        
        # gets spell element if none
        if element is None: element = self.element_handler.get_random_element()
        
        # gets spell firing modifiers
        launch_type = random.choice(['straight', 'lob', 'confused'])
        power -= self.spell_attributes['launch_type'][launch_type]
        spread_type = random.choice(['horizontal'])#, 'vertical'])
        power -= self.spell_attributes['spread_type'][spread_type]
        casting_type = random.choice(['from_self'])
        power -= self.spell_attributes['casting_type'][casting_type]
        
        # gets a series of spell options
        spell_options = {}
        for _ in range(100):
            spell = self.create_random_spell(power, element)
            spell_options[self.get_spell_cost(spell)] = spell
            
        closest, distance = None, 1e6
        for cost, spell in spell_options.items():
            test_distance = abs(power - cost)
            if test_distance < distance: closest, distance = spell, test_distance
        return closest
        
    def create_random_spell(self, power = 15, element = None):
        
        launch_type = random.choice(['straight', 'lob', 'confused'])
        spread_type = random.choice(['horizontal'])#, 'vertical'])
        casting_type = random.choice(['from_self'])
        
        # int types
        count = random.randint(1, 9)
        damage = random.randint(1, power if power < 100 else 99)
        
        # float types
        radius = random.uniform(0, power ** (1/3) if power ** (1/3) < 9.9 else 9.9)
        speed = random.uniform(5, 30)
        force = random.uniform(1, power ** (1/2) if power ** (1/2) else 9.9)
        angle = random.uniform(np.pi/24, np.pi/2)
        
        # element variables
        if element is None: element = self.element_handler.get_random_element()
        terrain_radius = radius / 3 * element.terrain
        color = element.color
        
        return Spell(self, damage, radius, terrain_radius, element, speed, force, spread_type, launch_type, casting_type, count, angle, True, color)
    
    def get_spell_cost(self, spell):
        
        cost = spell.damage * self.spell_attributes['damage']
        cost += (spell.radius * self.spell_attributes['radius']) ** 3
        cost += spell.speed * self.spell_attributes['speed']
        cost += (spell.force * self.spell_attributes['force']) ** 2
        
        cost *= spell.count
        return cost
    
    def update(self, delta_time):
        self.bullet_handler.update(delta_time)
    
class Spell():
    
    def __init__(self, spell_handler : SpellHandler, damage, radius, terrain_radius, element, speed, force = 0, spread_type = 'horizontal', launch_type = 'straight', casting_type = 'from_self', count = 1, angle = np.pi/3, destructive = False, color = (1.0, 1.0, 1.0)):
        
        # spell handler to make programs
        self.spell_handler = spell_handler
        
        # spell stats 
        self.damage = damage
        self.radius = radius
        self.terrain_radius = terrain_radius
        self.destructive = destructive
        self.force = force
        self.count = count
        
        # launch program variables
        self.launch_type = launch_type
        self.casting_type = casting_type
        self.spread_type = spread_type
        self.speed = speed
        self.angle = angle
        
        # visual variables
        self.color = color
        self.element = element
        
        # gets spread program
        if count == 1: self.spread_program = self.spell_handler.spread_handler.programs['single']
        else:
            match spread_type:
                case 'horizontal': self.spread_program = self.spell_handler.spread_handler.get_horizontal(count, angle)
                case 'vertical': self.spread_program = self.spell_handler.spread_handler.get_vertical(count, angle)
                case _: assert False, 'spread program does not exist'
                
        # gets casting program
        match casting_type:
            case 'from_self': self.casting_program = self.spell_handler.casting_handler.get_from_self(count)
            case _: assert False, 'casting program does not exist'
        
    # returns a list of bullets from the spell
    def get_bullets(self, pos, dir : np.array, caster):
        pos += [0, 0.5, 0]
        
        # gets all directions and positions of bullets fired
        match self.casting_type:
            case 'from_self': positions, directions = self.casting_program(pos, dir)
            case 'from_above': positions, directions = self.casting_program(..., dir)
            case _: assert False, 'casting type error when getting bulltes'
        directions = self.spread_program(directions)
        
        # returns a list of bullets using launch program
        match self.launch_type:
            case 'straight': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self, self.spell_handler.bullet_handler, positions[i], directions[i], self.spell_handler.launch_handler.get_straight(directions[i], self.speed), caster)) for i in range(len(positions))]
            case 'lob': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self, self.spell_handler.bullet_handler, positions[i], directions[i], self.spell_handler.launch_handler.get_lob(self.speed, -0.5), caster)) for i in range(len(positions))]
            case 'confused': return [self.spell_handler.bullet_handler.add_bullet(Bullet(self, self.spell_handler.bullet_handler, positions[i], directions[i], self.spell_handler.launch_handler.get_confused(directions[i], self.speed), caster)) for i in range(len(positions))]
            case _: assert False, 'launch program does not exist'
            