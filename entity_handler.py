from object_handler import *
from spell_handler import SpellHandler, Spell
from pathing_handler import PathingHandler
import pygame as pg
import glm

class EntityHandler():
    
    def __init__(self, object_handler : ObjectHandler, cam):
        
        self.object_handler = object_handler
        self.spell_handler = SpellHandler(object_handler)
        self.pathing_handler = PathingHandler()
        self.entities = []
        self.on_init(cam)
        
    def on_init(self, cam):
        
        # creates player
        player = Player(self, self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(10, 10, 10), scale=(.5, .5, .5))), cam, 100)
        self.entities.append(player)
        
        # creates starting enemies
        #self.entities.append(Enemy(self, self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(5, 5, 5), scale=(.5, .5, .5))), 100))
        
    def get_ragdoll_objects(self):
        
        return list(filter(lambda n: n.ragdoll, self.entities))
    
    def update(self, delta_time):
        
        # updates spells
        self.spell_handler.update(delta_time)
        
        # updates entities
        for entity in self.entities: 
            
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

class Entity():
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health, speed = 1, ragdoll = False):
        
        self.entity_handler = entity_handler
        self.ragdoll = ragdoll
        self.obj = obj
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
    
class Enemy(Entity):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, health, speed = 1, ragdoll = False, pathing_type = 'direct'):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll)
        
        match pathing_type:
            case 'direct': self.pathing = self.entity_handler.pathing_handler.get_direct(speed)
            case _: assert False, 'pathing type not recognized'
        
    def move(self, delta_time): 
        
        self.obj.set_pos(self.pathing(self.obj.pos, self.entity_handler.entities[0].obj.pos, delta_time))
        
class Player(Entity):
    
    def __init__(self, entity_handler : EntityHandler, obj : Object, cam, health, speed = 5, ragdoll = False):
        
        super().__init__(entity_handler, obj, health, speed, ragdoll)
        self.cam = cam
        self.spell = self.entity_handler.spell_handler.create_random_spell()
        
    def move(self, delta_time):
        
        velocity = self.speed * delta_time
        keys = pg.key.get_pressed()
        key_pressed = False
        if keys[pg.K_w]:
            self.obj.pos += glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
            key_pressed = True
        if keys[pg.K_s]:
            self.obj.pos -= glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
            key_pressed = True
        if keys[pg.K_a]:
            self.obj.pos -= self.cam.right * velocity
            key_pressed = True
        if keys[pg.K_d]:
            self.obj.pos += self.cam.right * velocity
            key_pressed = True
        if keys[pg.K_SPACE]:
            self.obj.hitbox.vel += glm.vec3(0, 50, 0) * delta_time
            key_pressed = True
            
        if key_pressed:
            self.obj.set_rot((0, -glm.radians(self.cam.yaw), 0))
            
    def set_camera(self, camera):
        self.cam = camera