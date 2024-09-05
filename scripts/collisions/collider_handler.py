import glm
from scripts.collisions.collider import Collider
from scripts.collisions.broad.bounding_volume_heirarchy import BoundingVolumeHeirarchy
from scripts.collisions.narrow.narrow_collisions import get_narrow_collision
from scripts.physics.impulse import calculate_collisions

class ColliderHandler():
    """controls import and interaction between colliders"""
    def __init__(self, scene) -> None:
        """stores imports and bodies"""
        self.scene = scene
        # vbos dictionary
        self.vbos = self.scene.vao_handler.vbo_handler.vbos
        self.colliders = []
        
    def add_collider(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None, vbo:str='cube', static = True, elasticity:float=0.1, kinetic_friction:float=0.4, static_friction:float=0.8):
        """adds new collider with corresponding object"""
        self.colliders.append(Collider(self, position, scale, rotation, vbo, static, elasticity, kinetic_friction, static_friction))
        return self.colliders[-1]
    
    def resolve_collisions(self):
        self.bvh.build_tree() # replace with better update system
        # loop through colliders and get possible collisions
        for collider1 in self.colliders:
            possible_colliders = self.bvh.get_collided(collider1)
            # determine narrow collisions
            for collider2 in possible_colliders:
                normal, distance, contact_points = get_narrow_collision(collider1.vertices, collider2.vertices, collider1.position, collider2.position)
                if distance == 0: continue # continue if no collision
                # immediately resolve penetration
                collection1 = collider1.collection
                collection2 = collider2.collection
                
                if collider1.static: 
                    collection2.position += normal * distance * 0.5
                else:
                    if collider2.static: 
                        collection1.position += normal * -distance * 0.5
                    else:
                        collection1.position += normal * -0.5 * distance * 0.5
                        collection2.position += normal * 0.5 * distance * 0.5
                #for both physics bodies
                if not (collection1.physics_body or collection2.physics_body): continue
                calculate_collisions(normal, collider1, collider2, collection1.physics_body, collection2.physics_body, contact_points, collection1.get_inverse_inertia(), collection2.get_inverse_inertia(), collection1.position, collection2.position)
    
    def get_model_matrix(self, data:list) -> glm.mat4:
        """gets projection matrix from object data"""
        # create blank matrix
        model_matrix = glm.mat4()
        # translate, rotate, and scale
        model_matrix = glm.translate(model_matrix, data[:3]) # translation
        model_matrix = glm.rotate(model_matrix, data[6], glm.vec3(-1, 0, 0)) # x rotation
        model_matrix = glm.rotate(model_matrix, data[7], glm.vec3(0, -1, 0)) # y rotation
        model_matrix = glm.rotate(model_matrix, data[8], glm.vec3(0, 0, -1)) # z rotation
        model_matrix = glm.scale(model_matrix, data[3:6]) # scale
        return model_matrix
    
    def get_real_vertex_locations(self, vbo) -> list:
        """gets the in-world locations of the collider vertices"""
        model_matrix = self.get_model_matrix()
        return [glm.vec3((new := glm.mul(model_matrix, (*vertex, 1)))[0], new[1], new[2]) for vertex in self.vbos[vbo].unique_points]

    def construct_bvh(self):
        self.bvh = BoundingVolumeHeirarchy(self)
        