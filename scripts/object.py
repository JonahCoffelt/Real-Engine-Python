from scripts.generic.data_types import vec3


CHUNK_SIZE = 40


class Object:
    def __init__(self, handler, vbo, texture, position: tuple, rotation: tuple, scale: tuple) -> None:
        # Rendering specifications
        self.handler = handler
        self.vbo     = vbo
        self.texture = texture

        # Chunk that the object is in
        self.chunk = (position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE)
        self.prev_chunk = self.chunk
        
        # Variables for detecting attribute changes
        self.prev_position = [0, 0, 0]
        self.prev_rotation = [0, 0, 0]
        self.prev_scale    = [1, 1, 1]

        # Model matrix vectors
        self.position = vec3(position, self.update_position)
        self.rotation = vec3(rotation, self.update_rotation)
        self.scale    = vec3(scale   , self.update_scale)  

    @property
    def position(self): return self._position
    @property
    def scale(self): return self._scale
    @property
    def rotation(self): return self._rotation
    @property
    def x(self): return self.position.x
    @property
    def y(self): return self.position.y
    @property
    def z(self): return self.position.z

    @position.setter
    def position(self, value):
        self._position = value
        self.update_position()
    @scale.setter
    def scale(self, value):
        self._scale = value
        self.update_scale()
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.update_rotation()
    @x.setter
    def x(self, value): self.position.x = value
    @y.setter
    def y(self, value): self.position.y = value
    @z.setter
    def z(self, value): self.position.z = value
    

    def update_position(self):
        self.chunk = (self.x // CHUNK_SIZE, self.y // CHUNK_SIZE, self.z // CHUNK_SIZE)

        if abs(self.prev_position[0] - self.position[0]) < 0.001 and abs(self.prev_position[1] - self.position[1]) < 0.001 and abs(self.prev_position[2] - self.position[2]) < 0.001: return False   

        if self.prev_chunk != self.chunk:
            if self.chunk not in self.handler.chunks:
                self.handler.chunks[self.chunk] = []
            
            self.handler.chunks[self.chunk].append(self)
            self.handler.chunks[self.prev_chunk].remove(self)

        self.handler.updated_chunks.add(self.prev_chunk)
        self.handler.updated_chunks.add(self.chunk)

        self.prev_chunk = self.chunk
        self.prev_position = self.position[:]

    def update_scale(self):
        if abs(self.prev_scale[0] - self.scale.x) < 0.001 and abs(self.prev_scale[1] - self.scale.y) < 0.001 and abs(self.prev_scale[2] - self.scale.z) < 0.001: return False  
        
        self.handler.updated_chunks.add(self.chunk)

        self.prev_scale = self.scale[:]

    def update_rotation(self):
        if abs(self.prev_rotation[0] - self.rotation.x) < 0.001 and abs(self.prev_rotation[1] - self.rotation.y) < 0.001 and abs(self.prev_rotation[2] - self.rotation.z) < 0.001: return False  
        
        self.handler.updated_chunks.add(self.chunk)

        self.prev_rotation = self.rotation[:]

    def __repr__(self) -> str:
        return f'<Object: {self.position[0]},{self.position[1]},{self.position[2]}>'