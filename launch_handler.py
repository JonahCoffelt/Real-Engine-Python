class LaunchHandler():
    
    def __init__(self):
        
        self.programs = {}
        
    # functions
    def get_straight(self, direction, speed):
        
        def program(pos, delta_time):
            return pos + direction * speed * delta_time
            
        return program
        
    def get_lob(self, direction, speed, gravity):
        
        def program(pos, delta_time):
            pos = pos + direction * speed * delta_time
            pos[1] -= gravity
            return pos
            
        return program