import glm

class SuperCollection():
    def __init__(self, collection_handler, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None, name:str=''):
        # collection function handler
        self.collection_handler = collection_handler
        # matrix data
        self.position = glm.vec3(position) if position else glm.vec3(0, 0, 0)
        self.scale    = glm.vec3(scale)    if scale    else glm.vec3(1, 1, 1)
        self.rotation = glm.vec3(rotation) if rotation else glm.vec3(0, 0, 0)
        # updating data
        self.prev_position = glm.vec3(self.position)
        self.prev_scale    = glm.vec3(self.scale)
        self.prev_rotation = glm.vec3(self.rotation)
        
        self.update_position = True
        self.update_scale    = True
        self.update_rotation = True
        
        self.update_inertia = True
        # info
        self.name = name
        
    # modifying data types
    def is_same_vec(self, vec1:list|glm.vec3, vec2:list|glm.vec3, epsilon:float=1e-7) -> bool:
        """
        Determines whether or not two vectors are far enough apart to be considered "similar".
        """
        return all(abs(v1 - v2) <= epsilon for v1, v2 in zip(vec1, vec2))
    
    def update(self) -> None:
        """
        Updates previous data if data exceeds error value
        """
        # position
        if self.update_position and self.is_same_vec(self.prev_position, self.position): 
            self.position        = glm.vec3(self.prev_position)
            self.update_position = False
        else: self.prev_position = glm.vec3(self.position)
        
        # scale
        if self.update_scale and self.is_same_vec(self.prev_scale, self.scale):
            self.scale        = glm.vec3(self.prev_scale)
            self.update_scale = False
        else: self.prev_scale = glm.vec3(self.scale)
        
        # rotation
        if self.update_rotation and self.is_same_vec(self.prev_rotation, self.rotation):
            self.rotation        = glm.vec3(self.prev_rotation)
            self.update_rotation = False
            self.update_inertia  = False
        else: self.prev_rotation = glm.vec3(self.rotation)
        
    def after_update(self) -> None:
        """
        Called after all updates have been completed for singles and collections
        """
        self.update_position = False
        self.update_rotation = False
        self.update_scale    = False

    # position
    @property
    def position(self): 
        return self._position
    
    @position.setter
    def position(self, value):
        self.update_position = True
        self._position       = value
    
    # scale
    @property
    def scale(self): 
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self.update_scale = True
        self._scale       = value
        
    # rotation
    @property
    def rotation(self): return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        self.update_rotation        = True
        self.update_rotation_matrix = True
        self._rotation              = value