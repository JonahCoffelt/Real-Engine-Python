from object_handler import *
import pygame as pg

class EntityHandler():
    
    def __init__(self, object_handler : ObjectHandler, cam):
        
        self.object_handler = object_handler
        self.entities = []
        self.on_init(cam)
        
    def on_init(self, cam):
        
        player = Player(self.object_handler.add_object(Object(self.object_handler, self.object_handler.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(randint(-10, 10), randint(0, 15), randint(-10, 10)), scale=(.5, .5, .5))), cam, 100)
        self.entities.append(player)
        
    def get_ragdoll_objects(self):
        
        return list(filter(lambda n: n.ragdoll, self.entities))
    
    def update(self, delta_time):
        
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
    
    def __init__(self, obj : Object, health, speed = 1, ragdoll = False):
        
        self.ragdoll = ragdoll
        self.obj = obj
        self.health = health
        self.speed = speed
        
    def move(self, delta_time): ...
        
class Player(Entity):
    
    def __init__(self, obj : Object, cam, health, speed = 5, ragdoll = False):
        
        super().__init__(obj, health, speed, ragdoll)
        self.cam = cam
        
    def move(self, delta_time):
        
        velocity = self.speed * delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.obj.pos += glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
        if keys[pg.K_s]:
            self.obj.pos -= glm.normalize(glm.vec3(self.cam.forward.x, 0, self.cam.forward.z)) * velocity
        if keys[pg.K_a]:
            self.obj.pos -= self.cam.right * velocity
        if keys[pg.K_d]:
            self.obj.pos += self.cam.right * velocity
        if keys[pg.K_SPACE]:
            self.obj.hitbox.vel += glm.vec3(0, 0.1, 0)
            
        self.obj.set_rot((0, -glm.radians(self.cam.yaw), 0))
            
    def set_camera(self, camera):
        self.cam = camera
        
class Enemy(Entity):
    
    def __init__(self, obj, health, ragdoll = False):
        
        super().__init__(obj, health, ragdoll)