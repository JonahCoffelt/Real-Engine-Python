from object_handler import *

class EntityHandler():
    
    def __init__(self):
        
        self.entities = []
        self.on_init()
        
    def on_init(self):
        ...
        
    def get_ragdoll_objects(self):
        
        return list(filter(lambda n: n.ragdoll, self.entities))

class Entity():
    
    def __init__(self, obj, health, ragdoll = False):
        
        self.ragdoll = ragdoll
        self.obj = obj
        self.health = health
        
class Player(Entity):
    
    def __init__(self, obj, health, ragdoll = False):
        
        super().__init__(obj, health, ragdoll)
        
class Enemy(Entity):
    
    def __init__(self, obj, health, ragdoll = False):
        
        super().__init__(obj, health, ragdoll)