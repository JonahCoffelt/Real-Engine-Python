import glm

class PathingHandler():
    
    def __init__(self):
        
        self.pathing_programs = {}
        
    # movs directly towards the target
    def get_direct(self, speed):
        
        def program(here, there, delta_time):
            there = [there[0], here[1], there[2]]
            return here + glm.normalize(there - here) * speed * delta_time
        return program
    
    # moves directly towards the target until its within a given radius
    def get_direct_distanced(self, speed, radius):
        
        def program(here, there, delta_time):
            there = [there[0], here[1], there[2]]
            direction = glm.normalize(there - here) * speed * delta_time
            if glm.length(there - here + direction) < radius: return here - direction
            return here + direction
        return program
    
    # runs away from the target regradless of distance
    def get_away(self, speed):
        
        def program(here, there, delta_time):
            there = [there[0], here[1], there[2]]
            return here - glm.normalize(there - here) * speed * delta_time
        return program