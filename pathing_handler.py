import glm

class PathingHandler():
    
    def __init__(self):
        
        self.pathing_programs = {}
        
    def get_direct(self, speed):
        
        def direct(here, there, delta_time):
            return here + glm.normalize(there - here) * speed * delta_time
        return direct