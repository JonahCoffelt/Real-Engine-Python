import glm
import numpy as np


class Hitbox():
    
    def __init__(self, obj, vertices, faces, dimensions, vel = (0, 0, 0), rot_vel = 0, rot_axis = (0, 0, 0)):
        
        # model
        self.obj = obj
        
        # for collision
        self.original_vertices = [glm.vec3(*vertex) for vertex in vertices]
        self.vertices = []
        self.normals = {}
        self.update_vertices()
        
        self.faces = faces
        self.dimensions = dimensions
        self.scale_dimensions()
        
        # movement
        self.vel = glm.vec3(vel)
        self.rot_vel = rot_vel
        self.rot_axis = glm.vec3(rot_axis)
        
    def scale_dimensions(self):
        
        self.dimensions = np.array([i for i in self.obj.scale * self.dimensions])
        
    def get_center(self):
        
        point = []
        for i in range(3):
            point.append(sum([vertex[i] for vertex in self.vertices]) / len(self.vertices))
        return glm.vec3(point)
    
    def update_vertices(self):
        
        self.vertices = [self.obj.model.m_model * vertex for vertex in self.original_vertices]
        self.normals = {}
    
    def move_tick(self, delta_time, acceleration : glm.vec3, rot_acceleration):
        
        if self.obj.immovable: return
        self.vel += delta_time * acceleration
        self.rot_vel += delta_time * rot_acceleration
        
    def move_tick_translate(self, delta_time, acceleration : glm.vec3):
        
        if self.obj.immovable: return
        self.vel += delta_time * acceleration
        
    def move_tick_rot(self, delta_time, rot_acceleration):
        
        if self.obj.immovable: return
        self.rot_vel += delta_time * rot_acceleration
        
    # gets corresponding vertex with face and face-vertex index
    def get_face_vertex(self, fi, vi):
        
        return self.vertices[self.faces[fi][vi]]
        
    # gets outward facing normal vector of the face
    def get_face_normal(self, index):
        
        # chacks memo
        if index in self.normals:
            return self.normals[index]
        
        # records to memo
        norm = glm.cross(self.get_face_vertex(index, 1) - self.get_face_vertex(index, 0), self.get_face_vertex(index, -1) - self.get_face_vertex(index, 0))
        self.normals[index] = norm
        return norm
    
    # setter methods
    def set_vel(self, vel): self.vel = glm.vec3(vel)
    def set_rot_vel(self, rot_vel): self.rot_vel = rot_vel
    def set_rot_axis(self, rot_axis): self.rot_axis = rot_axis
    
class LargeCubeHitbox(Hitbox):
    
    def __init__(self, obj, vel = (0, 0, 0), rot_vel = 0, rot_axis = (0, 0, 0)):
        
        super().__init__(obj,
            [(-2, -2, 2), (2, -2, 2), (2, 2, 2), (-2, 2, 2), (-2, 2, -2), (-2, -2, -2), (2, -2, -2), (2, 2, -2)],
            [(0, 2, 3), (0, 1, 2), (1, 7, 2), (1, 6, 7), (6, 5, 4), (4, 7, 6), (3, 4, 5), (3, 5, 0), (3, 7, 4), (3, 2, 7), (0, 6, 1), (0, 5, 6)],
            (2, 2, 2), vel, rot_vel, rot_axis)
        
class CubeHitbox(Hitbox):
    
    def __init__(self, obj, vel = (0, 0, 0), rot_vel = 0, rot_axis = (0, 0, 0)):
        
        super().__init__(obj,
            [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)],
            [(0, 2, 3), (0, 1, 2), (1, 7, 2), (1, 6, 7), (6, 5, 4), (4, 7, 6), (3, 4, 5), (3, 5, 0), (3, 7, 4), (3, 2, 7), (0, 6, 1), (0, 5, 6)],
            (2, 2, 2), vel, rot_vel, rot_axis)
        
class FittedHitbox(Hitbox):
    
    def __init__(self, obj, file_name : str, rectangular = False, vel = (0, 0, 0), rot_vel = 0, rot_axis = (0, 0, 0)):
        
        vertices, faces, mins, maxs = self.read_in_file(file_name)
        dimensions = [maxs[i] - mins[i] for i in range(3)]

        # super init for both rect and fitted
        if rectangular:
            super().__init__(obj,
                [(x, y, z) for z in (mins[2], maxs[2]) for y in (mins[1], maxs[1]) for x in (mins[0], maxs[0])], 
                [(0, 2, 3), (0, 1, 2), (1, 7, 2), (1, 6, 7), (6, 5, 4), (4, 7, 6), (3, 4, 5), (3, 5, 0), (3, 7, 4), (3, 2, 7), (0, 6, 1), (0, 5, 6)],
                dimensions, vel, rot_vel, rot_axis)
        else:
            super().__init__(obj, vertices, faces, dimensions, vel, rot_vel, rot_axis)
            
    def read_in_file(self, file_name):
        
        # load in file
        lines = []

        with open(f'objects/{file_name}.obj') as obj_file:
            lines = obj_file.readlines()
            
        # gets vertices and faces
        vertices = []
        faces = []
        
        # dimensions
        mins, maxs = [1e6, 1e6, 1e6], [-1e6, -1e6, -1e6]
        
        # fill list of vertices and faces
        for line in lines:
            head = line[0:2]
            if head == 'v ':
                
                # adds vertex to list of vertices
                coords = [float(i) for i in line[2:].split()]
                vertices.append(glm.vec3(coords))
                
                # determines dimensions of model
                for i in range(3):
                    mins[i] = min(coords[i], mins[i])
                    maxs[i] = max(coords[i], maxs[i])
                
            elif head == 'f ':
                faces.append([int(i.split('/')[0]) - 1 for i in line[2:].split()]) # gets vertex indices
                
        return vertices, faces, mins, maxs