from object_handler import Object
from model import BaseModel

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
    
    def __init__(self, spell, bullet_handler : BulletHandler, pos, launch_program):
        
        # hierarchy variables
        self.spell = spell
        self.launch_program = launch_program
        self.bullet_handler = bullet_handler
        
        self.obj = self.bullet_handler.object_handler.add_object(Object(self.bullet_handler.object_handler, self.bullet_handler.object_handler.scene, BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos = pos, rot = (0, 0, 0), scale=(.2, .2, .2), gravity = False, immovable = True))
        
    def move(self, delta_time):
        
        # checks if bullet has collided
        if self.obj.last_collided is not None:
            self.execute()
            return
        
        self.obj.set_pos(self.launch_program(self.obj.pos, delta_time))
        
    def get_particle(self):
        
        ...
        
    def execute(self):
        
        # bullet aftermath
        self.bullet_handler.object_handler.scene.chunk_handler.modify_terrain(-self.spell.radius, self.obj.pos)
        
        # removes bullet from game
        self.remove_self()
        
    def remove_self(self):
        
        # removes from handler lists
        self.bullet_handler.bullets.remove(self)
        self.bullet_handler.object_handler.objects.remove(self.obj)
        
        # delete self from system
        del self.obj
        del self