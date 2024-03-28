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
    
    def is_same_spell(self, obj1, obj2):
        
        spell = None
        objs = [obj1, obj2]
        for bullet in self.bullets:
            if not len(objs): break
            for obj in objs:
                if obj is bullet.obj:
                    if spell is None: spell = bullet.spell
                    elif spell is bullet.spell: return True
                    else: return False
                    break
        else: assert False, 'uh oh'
        
class Bullet():
    
    def __init__(self, spell, bullet_handler : BulletHandler, pos, launch_program):
        
        # hierarchy variables
        self.spell = spell
        self.launch_program = launch_program
        self.bullet_handler = bullet_handler
        
        # visual variables
        self.obj = self.bullet_handler.object_handler.add_object(Object(self.bullet_handler.object_handler, self.bullet_handler.object_handler.scene, BaseModel, program_name='default', material='wooden_box', obj_type='wooden_box', pos = pos, rot = (0, 0, 0), scale=(.2, .2, .2), gravity = False, immovable = False))
        self.particle_timer = 0
        
    def move(self, delta_time):
        
        # checks if bullet has collided
        if self.obj.last_collided is not None:
            self.execute()
            return
        
        # visuals
        if self.particle_timer > 0.2:
            #self.spawn_particle()
            self.particle_timer = 0
        self.particle_timer += delta_time
        
        # movement
        self.obj.set_pos(self.launch_program(self.obj.pos, delta_time))
        
    def spawn_particle(self):
        
        self.bullet_handler.object_handler.scene.particle_handler.add_particle(clr = self.spell.color, pos = self.obj.pos, vel = (0, 0, 0), accel = (0, 0, 0))
        
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