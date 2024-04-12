from object_handler import *
from spell_handler import SpellHandler, Spell
from pathing_handler import PathingHandler
import pygame as pg
import glm
from random import choice, uniform
from config import config
import cudart


class EntityHandler():
    
    def __init__(self, object_handler : ObjectHandler, cam):
        
        self.object_handler = object_handler
        self.spell_handler = SpellHandler(object_handler)
        self.pathing_handler = PathingHandler()
        self.entities = []
        self.on_init(cam)
        
    def on_init(self, cam):
        
        # creates player
        player = Player(self, self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(uniform(20, 100), 30, uniform(20, 100)), scale=(.5, .5, .5))), cam, 100)
        self.entities.append(player)
        
        # creates starting enemies
        for _ in range(0):
            self.entities.append(SpellCaster(self, self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(uniform(20, 100), 30, uniform(20, 100)), scale=(.5, .5, .5))), 100, speed = 4))
        
    def get_ragdoll_objects(self):
        
        return list(filter(lambda n: n.ragdoll, self.entities))
    
    def update(self, delta_time):
        
        # updates spells
        self.spell_handler.update(delta_time)
        
        # updates entities
        for entity in self.entities: 
            
            # swaps from ragdoll and back
            if glm.length(entity.obj.hitbox.vel) > (1 if entity.ragdoll else 3) or entity.obj.hitbox.rot_vel > 0.25: entity.ragdoll = True # and not entity.obj.on_side()
            else: entity.ragdoll = False
            
            # ragdoll
            if entity.ragdoll: 
                ...
            else: 
                
                # sets velocities to zero
                for i in (0, 2): entity.obj.hitbox.vel[i] = 0
                entity.obj.hitbox.rot_vel = 0
            
            # moves entity based on AI, controls, etc
            entity.move(delta_time)
        
    def set_player_camera(self, camera):
        self.entities[0].set_camera(camera)
        
    def get_entities_in_radius(self, pos, radius):
        
        in_range = {}
        for entity in self.entities:
            direction = entity.obj.pos - pos
            if glm.length(direction) <= radius: in_range[entity] = glm.normalize(direction)
        return in_range

class Entity():
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health, speed = 1, ragdoll = False):
        
        self.entity_handler = entity_handler
        self.ragdoll = ragdoll
        self.obj = obj
        self.max_health = health
        self.health = health
        self.speed = speed
        
    def move(self, delta_time): ...
    
    def take_hit(self, spell : Spell, origin):
        
        # spell effects
        self.health -= spell.damage
        
        # force
        direction = glm.normalize(self.obj.pos - origin)
        self.obj.hitbox.set_vel(direction * spell.force)
        
        # after checks
        if self.health <= 0:
            self.on_death()
        
    def on_death(self):
        
        self.remove_self()
        
    def remove_self(self):
        
        # removes from handler lists
        self.entity_handler.entities.remove(self)
        self.entity_handler.object_handler.objects.remove(self.obj)
        
        # delete just in case
        del self.obj
        del self
        
    # def ray_cast_vec(self, origin, vec, tests = 100, multiplier = 1, starting_test = 0):
    def can_see(self, target):
        
        direction = (target.pos - self.obj.pos) / 100
        # detects if target is in line of sight
        return self.entity_handler.object_handler.scene.chunk_handler.ray_cast_vec(self.obj.pos, direction, starting_test = 30) is None
    
    # default to aiming at player
    def get_aiming_at(self):
        
        if self.can_see(self.entity_handler.entities[0].obj): return self.entity_handler.entities[0].obj.pos
        else: glm.vec3(0, 0 ,0) # fix
        
class Player(Entity):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, cam, health, speed = 5, ragdoll = False):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll)
        self.cam = cam
        self.spell = self.entity_handler.spell_handler.create_random_spell()
        
    def move(self, delta_time):
        
        keys = pg.key.get_pressed()
        if keys[config['controls']['up']] and self.obj.last_collided is not None:
            
            # launches player with rotation
            direction = glm.normalize(glm.vec3(np.cos(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch)), np.sin(np.deg2rad(self.cam.pitch)), np.sin(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch))))
            self.obj.hitbox.rot_axis = glm.normalize(glm.cross(direction, (0, 1, 0)))
            self.obj.hitbox.vel = direction * 5
            self.obj.hitbox.rot_vel = np.pi
            self.ragdoll = True
        
        if self.ragdoll: return
        
        velocity = self.speed * delta_time
        key_pressed = False
        if keys[config['controls']['forward']]:
            self.obj.pos += glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
            key_pressed = True
        if keys[config['controls']['backward']]:
            self.obj.pos -= glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
            key_pressed = True
        if keys[config['controls']['left']]:
            self.obj.pos -= self.cam.right * velocity
            key_pressed = True
        if keys[config['controls']['right']]:
            self.obj.pos += self.cam.right * velocity
            key_pressed = True
            
        if key_pressed:
            self.obj.set_rot([0, -glm.radians(self.cam.yaw), 0])
            
    def set_camera(self, camera):
        self.cam = camera
        
class Enemy(Entity):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health = 50, speed = 3, ragdoll = False, pathing_type = 'direct'):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll)
        match pathing_type:
            case 'direct': self.pathing = self.entity_handler.pathing_handler.get_direct(speed)
            case _: assert False, 'pathing type not recognized'
        self.knows_player_location = False
        self.max_forget_time = 5
        self.forget_time = 5
        
    def move(self, delta_time): 
        
        # do nothing if in ragdoll
        if self.ragdoll: return
        self.obj.set_pos(self.pathing(self.obj.pos, self.entity_handler.entities[0].obj.pos, delta_time))
        
        can_see_player = self.can_see(self.entity_handler.entities[0].obj)
        if can_see_player:
            self.knows_player_location = True
            self.forget_time = self.max_forget_time
        
        if self.knows_player_location:
            self.obj.set_pos(self.pathing(self.obj.pos, self.entity_handler.entities[0].obj.pos, delta_time))
            if not can_see_player: self.forget_time -= delta_time
            if self.forget_time <= 0: self.knows_player_location = False
        
class SpellCaster(Enemy):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health = 50, speed = 3, ragdoll = False, pathing = 'direct', power = 0, spells : list = [], max_cooldown = 5):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll, pathing)
        self.max_cooldown = max_cooldown
        self.cooldown = max_cooldown
        self.spells = spells
        self.on_init(power)
        
    def on_init(self, power):
        
        self.spells.append(self.entity_handler.spell_handler.create_random_spell())
        
    def move(self, delta_time):
        
        # reduces spell cooldown time
        self.cooldown -= delta_time
        
        super().move(delta_time)
        
        # spell casting
        if self.cooldown < 0:
            if self.can_see(self.entity_handler.entities[0].obj):
                direction = glm.normalize(self.entity_handler.entities[0].obj.pos - self.obj.pos)
                choice(self.spells).get_bullets(self.obj.pos + direction * 2, np.array([i for i in direction]), self)
                self.cooldown = self.max_cooldown
            else: self.cooldown += 0.5