import glm
from scripts.collections.super_collection import SuperCollection
from scripts.collections.single import Single
from scripts.generic.math_functions import get_model_matrix, get_rotation_matrix
    
# collection that can contain multiple of each object
class Collection(SuperCollection):
    def __init__(self, collection_handler, position:glm.vec3|list=None, scale:glm.vec3|list=None, rotation:glm.vec3|list=None, collections:list=None, physics_body=None, name:str='') -> None:
        super().__init__(collection_handler, position, scale, rotation, name)
        # child collections
        self.collections:list[Collection|Single] = collections if collections else []
        # for physics
        self.model_matrix = get_model_matrix(self.position, self.scale, self.rotation)
        self.physics_body = physics_body
        # align children
        self.sync_data()
        # after children sync init
        self.aligned_inertia = self.define_inverse_inertia()
        self.inverse_inertia = self.get_inverse_inertia()
    
    # initialization
    def init_physics_body(self):
        self.remove_physics_bodies()
        if self.physics_body: self.physics_body.rotation = glm.quat(self.rotation)
        
    def remove_physics_bodies(self) -> None:
        for collection in self.collections: collection.remove_physics_bodies()
    
    # updating
    def update(self, delta_time:float) -> None:
        super().update()
        # update variables from last movement
        if self.update_position or self.update_scale or self.update_rotation:
            self.model_matrix = get_model_matrix(self.position, self.scale, self.rotation)
        # update physics body
        if self.physics_body:
            self.position       += self.physics_body.get_delta_position(delta_time)
            self.rotation        = self.physics_body.get_new_rotation(delta_time)
            self.rotation_matrix = get_rotation_matrix(self.rotation)
            self.sync_data() 
        
            
    def sync_data(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None) -> None:
        """
        Synchronizes the position, scale, and rotation of all child collections. Data may be inherited by a parent. 
        """
        if self.position.y < self.collection_handler.death_plane: 
            self.position = glm.vec3(5, 5, 5)
            if self.physics_body: 
                self.physics_body.velocity = glm.vec3(0, 0, 0)
                self.physics_body.rotational_velocity = 0
                
        if position or scale or rotation: ... # TODO: add collection recursion
        else: 
            for collection in self.collections: 
                new_position = glm.mul(self.model_matrix, (*collection.position, 1))
                collection.sync_data(glm.vec3([*new_position][:3]), self.scale, self.rotation)
    
    # getter methods 
    def get_colliders(self):
        colliders = []
        for collection in self.collections: colliders += collection.get_colliders()
        return colliders
    
    def get_objects(self):
        objects = []
        for collection in self.collections: objects += collection.get_objects()
        return objects
    
    def get_objects_with_path(self):
        names   = []
        objects = []
        for collection in self.collections: 
            name, object = collection.get_objects_with_path()
            names       += name
            objects     += object
        return [f'{self.name}>{name}' for name in names], objects
    
    def add_collection(self, collection): self.collections.append(collection)
    
    # physics function
    def define_inverse_inertia(self) -> glm.mat3x3:
        inertia_data = [(collection.get_inverse_inertia(), collection.position) for collection in self.collections]
        inverse_inertia = glm.mat3x3(0.0)
        # sum child inertia tensors
        for inertia in inertia_data:
            if not inertia[0]: continue # moves on if inertia tensor does not exist
            child_inertia      = glm.inverse(inertia[0])
            child_displacement = inertia[1]
            inverse_inertia   += child_inertia + (glm.dot(child_displacement, child_displacement) * glm.mat3x3() - glm.outerProduct(child_displacement, child_displacement))
        # return the inverse of the new inertia
        return glm.inverse(inverse_inertia) #TODO add parallel axis theorm for mesh center
    
    def get_inverse_inertia(self):
        """
        Returns the inverse inertia tensor with the proper scaling and rotations
        """
        # gets the new inverse inertia if rotation has been changed. 
        if self.update_inertia: 
            rotation_matrix      = get_rotation_matrix(self.rotation) 
            self.inverse_inertia = rotation_matrix * self.aligned_inertia * glm.transpose(rotation_matrix) * (1/self.physics_body.mass if self.physics_body else 1)
            self.update_inertia  = False
            
        # return transformed inertia tensor
        return self.inverse_inertia
