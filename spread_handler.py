import numpy as np

class SpreadHandler():
    
    def __init__(self):
            
        self.programs = {}
        self.on_init()
    
    def on_init(self):
        
        # speard program for single shot
        def single(directions):
            return directions
        self.programs['single'] = single
        
    # functions - return list of directions
    def get_horizontal(self, count, angle):
        
        angles = self.get_angles(count, angle)
        rot_mats = [self.get_xz_rot_mat(a) for a in angles]
        
        def program(directions):
            return [np.array([float(i) for i in rot_mats[i] * directions[i].reshape((3, 1))]) for i in range(count)]
        return program
        
    def get_vertical(self, count, angle):
        
        angles = self.get_angles(count, angle)
        rot_mats = [self.get_xy_rot_mat(a) for a in angles]
        
        def program(directions):
            return [np.array([float(i) for i in rot_mats[i] * directions[i].reshape((3, 1))]) for i in range(count)]
        return program
        
    # returns a list of angles to rotate a directional vector
    def get_angles(self, count, angle):
        step, a = 2 / (count - 1), angle/2
        return [(-1 + i * step) * a for i in range(count)]
        
    def get_xz_rot_mat(self, angle):
        return np.matrix([[np.cos(angle), 0, np.sin(angle)], 
                         [0, 1, 0],
                         [-np.sin(angle), 0, np.cos(angle)]])
        
    def get_xy_rot_mat(self, angle):
        return np.matrix([[np.cos(angle), -np.sin(angle), 0], 
                         [np.sin(angle), 0, np.cos(angle)], 
                         [0, 0, 1]])