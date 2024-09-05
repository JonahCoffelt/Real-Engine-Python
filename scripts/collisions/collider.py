import glm
from scripts.generic.math_functions import get_aabb_collision
from scripts.generic.math_functions import get_model_matrix

class Collider():
    def __init__(self, collider_handler, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None, vbo:str='cube', static = True, elasticity:float=0.1, kinetic_friction:float=0.4, static_friction:float=0.8) -> None:
        # parents
        self.collection       = None
        self.collider_handler = collider_handler
        # general data
        self.position = glm.vec3(position) if position else glm.vec3(0, 0, 0)
        self.scale    = glm.vec3(scale)    if scale    else glm.vec3(1, 1, 1)
        self.rotation = glm.vec3(rotation) if rotation else glm.vec3(0, 0, 0)
        # mesh
        self.vbo = self.collider_handler.vbos[vbo]
        # geometry
        self.update_vertices() # vertices must be created before everything else
        self.update_dimensions()
        self.update_geometric_center()
        # collisions
        self.update_aabb()
        self.parent = None
        # physics
        self.base_volume      = 8
        self.static           = static
        self.elasticity       = elasticity
        self.static_friction  = kinetic_friction
        self.kinetic_friction = static_friction
        
    def update_dimensions(self):
        minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
        for point in self.vertices:
            for i in range(3):
                if point[i] * self.scale[i] > maximums[i]: maximums[i] = point[i] * self.scale[i]
                if point[i] * self.scale[i] < minimums[i]: minimums[i] = point[i] * self.scale[i]
        self.dimensions = glm.vec3(*[(maximums[i] - minimums[i]) for i in range(3)])
        # print(self.dimensions)
        
    def update_vertices(self):
        model_matrix = get_model_matrix(self.position, self.scale, self.rotation)
        self.vertices = [glm.vec3((new := glm.mul(model_matrix, (*[float(f) for f in vertex], 1)))[0], new[1], new[2]) for vertex in self.vbo.unique_points]
        
    def update_geometric_center(self):
        minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
        for point in self.vertices:
            for i in range(3):
                if point[i] > maximums[i]: maximums[i] = point[i]
                if point[i] < minimums[i]: minimums[i] = point[i]
        self.geometric_center = glm.vec3([(maximums[i] + minimums[i])/2 for i in range(3)])
    
    def get_volume(self) -> float:
        return self.base_volume * self.scale.x * self.scale.y * self.scale.z
    
    def update_aabb(self) -> None:
        self.top_right    = self.geometric_center + self.dimensions / 2
        self.bottom_left  = self.geometric_center - self.dimensions / 2
        diff              = self.top_right - self.bottom_left
        self.surface_area = 2 * (diff.x * diff.y + diff.y * diff.z + diff.z * diff.x)
        
    # for broad stroke collision detection
    def find_sibling(self, collider, c_best, inherited):
        # compute lowest cost
        return self.get_test_surface(collider) + inherited, self
    
    def get_collided(self, collider):
        if self.collection is not collider.collection and get_aabb_collision(self.top_right, self.bottom_left, collider.top_right, collider.bottom_left): return [self] # do not need to check is self since they will have the same collection
        return []
    
    def get_test_surface(self, test_volume) -> float:
        """
        Gets the surface area of the aabb and the test volume
        Args:
            test_volume (float): either an aabb or collider
        """
        top_right         = glm.max(self.top_right, test_volume.top_right)
        bottom_left       = glm.min(self.bottom_left, test_volume.bottom_left)
        diff              = top_right - bottom_left
        return 2 * (diff.x * diff.y + diff.y * diff.z + diff.z * diff.x)