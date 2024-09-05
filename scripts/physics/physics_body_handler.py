import glm

class PhysicsBodyHandler():
    def __init__(self, scene, physics_bodies:list = None) -> None:
        self.scene           = scene
        self.physics_handler = self.scene.project.physics_handler
        self.physics_bodies  = physics_bodies if physics_bodies else []
        
    def add_physics_body(self, mass:float = 1, velocity:glm.vec3 = None, rotational_velocity:int = 0, axis_of_rotation:glm.vec3 = None):
        # add physics body and return
        self.physics_bodies.append(PhysicsBody(self, mass, velocity, rotational_velocity, axis_of_rotation))
        return self.physics_bodies[-1]
    
class PointPhysicsBody():
    def __init__(self, physics_body_handler:PhysicsBodyHandler, mass:float = 1, velocity:glm.vec3 = None) -> None:
        self.mass                 = mass
        self.physics_body_handler = physics_body_handler
        self.velocity             = velocity if velocity else glm.vec3(0, 0, 0)
        
    def get_delta_position(self, delta_time:float) -> glm.vec3:
        """
        gets the new position based on rk4. sets own velocity. 
        """
        # gets delta position and velocity from rk4
        delta_position, delta_velocity = self.physics_body_handler.physics_handler.get_constant_rk4(delta_time, self.velocity)
        
        # sets velocity and returns position to collection
        self.velocity += delta_velocity
        return delta_position

class PhysicsBody(PointPhysicsBody):
    def __init__(self, physics_body_handler:PhysicsBodyHandler, mass:float = 1, velocity:glm.vec3 = None, rotational_velocity:int = 0, axis_of_rotation:glm.vec3 = None) -> None:
        super().__init__(physics_body_handler, mass, velocity)
        self.rotational_velocity = rotational_velocity
        self.axis_of_rotation    = glm.vec3(axis_of_rotation) if axis_of_rotation else glm.vec3(1, 0, 0)
        self.rotation            = glm.quat((0, 0, 0)) # will be reset in collection's after init

    def get_new_rotation(self, delta_time: float):
        """
        returns the new rotation of the object after time
        """
        # get change in angle
        theta = -self.rotational_velocity * delta_time # negative for ccw which is positive
        
        # calculate rotation quaternion
        axis_world = glm.normalize(self.axis_of_rotation) if glm.length(self.axis_of_rotation) > 0 else glm.vec3(1, 0, 0)
        rq         = glm.angleAxis(theta, axis_world)
        
        # calculate and return using quaternions
        self.rotation = self.rotation * rq
        return glm.eulerAngles(self.rotation)
