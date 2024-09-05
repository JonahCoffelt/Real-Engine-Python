import glm

class PhysicsHandler:
    """controls the movement of physics bodies"""
    def __init__(self, scene = None, accelerations:list = [glm.vec3(0, -9.8, 0)]) -> None:
        """stores scene and accelerations list in project"""
        self.scene = scene
        self.accelerations = accelerations # constant accelerations in the scene
        
    def update(self, delta_time:float) -> None:
        """moves physics bodies and collections"""
        # update physics bodies 
        if self.scene is None: return # when project has no scene
        # accelerate all physics bodies by external accelerations
        self.scene.collection_handler.update(delta_time)
        self.scene.collider_handler.resolve_collisions()
        self.scene.skeleton_handler.update(delta_time)
        
    def get_constant_rk4(self, delta_time, velocity) -> tuple[glm.vec3, glm.vec3]:
        """Gives the delta position and velcoity of an object depending on the physics engine accelerations"""
        # sums accelerations
        acceleration = glm.vec3(0, 0, 0)
        for a in self.accelerations: acceleration += a
        # calculate rk4
        k1_pos = velocity
        k2_pos = velocity + 0.5 * delta_time * acceleration
        k3_pos = velocity + 0.5 * delta_time * acceleration
        k4_pos = velocity + delta_time * acceleration
        return (delta_time / 6) * (k1_pos + 2 * k2_pos + 2 * k3_pos + k4_pos), delta_time * acceleration
        
