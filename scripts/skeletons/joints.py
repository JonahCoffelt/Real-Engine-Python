import glm
from math import sqrt
from scripts.collections.collection import Collection

# child free to move and rotate within radius
class Joint(): 
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e3, min_radius:float=0, max_radius:float=1): # parent and child not saved for splitting
        # offsets from collection position
        self.parent_offset = glm.vec3(parent_offset)
        self.child_offset  = glm.length(child_offset) # radial joint
        # spring 
        self.spring_constant = spring_constant
        self.min_radius      = min_radius # the minimum radius the child collection can be from its offset
        self.max_radius      = max_radius
        
    def restrict(self, parent:Collection, child:Collection, delta_time:float) -> None:
        """
        Restricts the child to the parent using rk4
        """
        origin       = parent.position + self.parent_offset
        displacement = origin - child.position
        if glm.length(displacement) < 1e-7: return
        direction    = glm.normalize(displacement)
        
        # if the collection has a physics body do this
        if child.physics_body:
            
            # acceleration = self.get_spring_acceleration(child, direction, origin)
            # velocity     = child.physics_body.velocity
            # position     = child.position
            
            # k1_pos, k1_vel = delta_time * velocity,                  delta_time * acceleration(position)
            # k2_pos, k2_vel = delta_time * (velocity + 0.5 * k1_vel), delta_time * acceleration(position + 0.5 * k1_pos)
            # k3_pos, k3_vel = delta_time * (velocity + 0.5 * k2_vel), delta_time * acceleration(position + 0.5 * k2_pos)
            # k4_pos, k4_vel = delta_time * (velocity + k3_vel),       delta_time * acceleration(position + k3_pos)
            
            # child.position              += (k1_pos + 2 * k2_pos + 2 * k3_pos + k4_pos) / 6
            # child.physics_body.velocity += (k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel) / 6
            
            # print((k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel) / 6)
            
            force_spring = self.spring_constant * direction * (glm.length(origin - child.position) - self.child_offset)
            force_dampen = -sqrt(self.spring_constant * child.physics_body.mass) * child.physics_body.velocity
            acceleration = (force_spring + force_dampen) / child.physics_body.mass
            
            
            child.physics_body.velocity += acceleration * delta_time
            child.position += child.physics_body.velocity * delta_time
            
        # snap to position if it does not
        else: child.position = origin + direction * self.child_offset
    
    def get_spring_acceleration(self, constant_child:Collection, direction:glm.vec3, origin:glm.vec3):
        """
        Creates an acceleration function for spring joints
        """
        
        def acceleration(position:glm.vec3) -> glm.vec3:
            return -self.spring_constant * direction * (glm.length(origin - position) - self.child_offset) / constant_child.physics_body.mass
        
        return acceleration
        
# child free to move within radius, child must point at offset
class BallJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)
    
# child is locked in place but can rotate on given axis TODO change params
class RotatorJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)
        
# child free to move within radius but can only rotate on given axis TODO change params
class HingeJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)

# child cannot move or be rotated ex pistons
class LockedJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)