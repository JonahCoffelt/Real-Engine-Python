import random

class LaunchHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    # functions
    def get_straight(self, direction, speed):
        
        def program(pos, dir, delta_time):
            return pos + direction * speed * delta_time, dir
        return program
    
    def get_lob(self, speed, gravity):
        
        def program(pos, dir, delta_time):
            pos += dir * speed * delta_time
            dir[1] += gravity * delta_time
            return pos, dir
        return program
    
    # adds randomness to spells movement
    def get_confused(self, direction, speed):
        
        def program(pos, dir, delta_time):
            return pos + [(i * speed + random.uniform(-0.8, 0.8) * speed) * delta_time for i in direction], dir
        return program