import glm
from scripts.generic.math_functions import get_aabb_collision

class AABB():
    def __init__(self, a, b, parent):
        """
        Initializes a AABB from a collider or another AABB. 
        """
        self.a = a
        self.b = b
        self.parent = parent
        self.update_points()
        self.update_surface_area()
        
    def update_points(self):
        """
        Gets the top ritgh and bottom left points of the AABB
        """
        self.top_right   = glm.max(self.a.top_right, self.b.top_right)
        self.bottom_left = glm.min(self.a.bottom_left, self.b.bottom_left)
    
    # surface area calculations
    def update_surface_area(self):
        """
        Updates the surface area of the AABB, extreme points need to be updated first
        """
        diff              = self.top_right - self.bottom_left
        self.surface_area = 2 * (diff.x * diff.y + diff.y * diff.z + diff.z * diff.x)
        
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
        
    def get_delta_test_surface(self, test_volume) -> float:
        return self.get_test_surface(test_volume) - self.surface_area


    def find_sibling(self, collider, c_best, inherited):
        # compute lowest cost
        c = self.get_test_surface(collider) + inherited
        if c < c_best: c_best = c
        
        # determine if children are a viable option
        delta_c = self.get_delta_test_surface(collider)
        c_low   = collider.surface_area + delta_c + inherited
        
        # investigate chlidren
        best_aabb = self
        if c_low < c_best:
            # check a for better c value
            child_c, child_aabb = self.a.find_sibling(collider, c_best, inherited + delta_c)
            if child_c < c_best: c_best, best_aabb = child_c, child_aabb
            
            # check b for better c value
            child_c, child_aabb = self.b.find_sibling(collider, c_best, inherited + delta_c)
            if child_c < c_best: c_best, best_aabb = child_c, child_aabb
            
        return c_best, best_aabb
    
    def get_collided(self, collider) -> list:
        # check for overlap with self
        if not get_aabb_collision(self.top_right, self.bottom_left, collider.top_right, collider.bottom_left): return []
        # if a success was detected, run aabb on children
        return self.a.get_collided(collider) + self.b.get_collided(collider)
            
    @property
    def a(self): return self._a
    
    @a.setter
    def a(self, value):
        if not isinstance(value, AABB): value.parent = self # if it's a collider set parent to self
        self._a = value
        
    @property
    def b(self): return self._b
    
    @b.setter
    def b(self, value):
        if not isinstance(value, AABB): value.parent = self # if it's a collider set parent to self
        self._b = value