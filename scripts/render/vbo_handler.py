import os
import numpy as np
from pyobjloader import load_model
#from scripts.model import load_model
from numba import njit


class VBOHandler:
    """
    Stores all vertex buffer objects
    """
    def __init__(self, ctx, directory='models'):
        self.ctx = ctx
        self.directory = directory
        self.vbos = {}
        self.vbos['cube'] = CubeVBO(self.ctx)
        self.vbos['frame'] = FrameVBO(self.ctx)

        for file in os.listdir(self.directory):
            filename = os.fsdecode(file)

            if not filename.endswith(".obj"): continue

            obj_file = os.path.join(directory, filename)
            self.vbos[file[:-4]] = ModelVBO(self.ctx, obj_file)

    def release(self):
        """
        Releases all VBOs in handler
        """

        [vbo.vbo.release() for vbo in self.vbos.values()]


class BaseVBO:
    """
    Stores vertex data, format, and attributes for VBO
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.unique_points: list
        self.format: str = None
        self.attrib: list = None

    def get_vertex_data(self) -> np.ndarray: ...

    @staticmethod
    def get_data(verticies, indicies) -> np.ndarray:
        """
        Formats verticies based on indicies
        """
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        """
        Creates a buffer with the vertex data
        """
        
        self.vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(self.vertex_data)

        verticies = self.vertex_data[:,:3]

        self.unique_points = []
        [self.unique_points.append(x) for x in verticies.tolist() if x not in self.unique_points]

        # Save the mash vertex indicies for softbody reconstruction
        self.mesh_indicies = np.zeros(shape=(len(self.vertex_data)))
        for i, vertex in enumerate(self.vertex_data):
            index = self.unique_points.index(vertex[:3].tolist())
            self.mesh_indicies[i] = index

        self.unique_points = np.array(self.unique_points, dtype='f4')

        return vbo

    
class CubeVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 2f 3f'
        self.attribs = ['in_position', 'in_uv', 'in_normal']

    def get_vertex_data(self):
        verticies = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                     (-1,  1,-1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]
        
        indicies = [(0, 2, 3), (0, 1, 2),
                    (1, 7, 2), (1, 6, 7),
                    (6, 5, 4), (4, 7, 6),
                    (3, 4, 5), (3, 5, 0),
                    (3, 7, 4), (3, 2, 7),
                    (0, 6, 1), (0, 5, 6)]

        vertex_data = self.get_data(verticies, indicies)

        tex_coord_verticies = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indicies = [(0, 2, 3), (0, 1, 2),
                              (0, 2, 3), (0, 1, 2),
                              (0, 1, 2), (2, 3, 0),
                              (2, 3, 0), (2, 0, 1),
                              (0, 2, 3), (0, 1, 2),
                              (3, 1, 2), (3, 0, 1)]
        tex_coord_data = self.get_data(tex_coord_verticies, tex_coord_indicies)

        normals = [(0, 0,  1) * 6,
                   ( 1, 0, 0) * 6,
                   (0, 0, -1) * 6,
                   (-1, 0, 0) * 6,
                   (0,  1, 0) * 6,
                   (0, -1, 0) * 6]
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        vertex_data = np.hstack([vertex_data, tex_coord_data])
        vertex_data = np.hstack([vertex_data, normals])
        return vertex_data
    

class FrameVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 2f'
        self.attribs = ['in_position', 'in_uv']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],  # Bottom Left
                     [ 1, -1, 0],  # Bottom Right
                     [ 1, 1, 0],   # Top Right
                     [-1, 1, 0],  # Top Left
                     ])
        indicies = [(3, 0, 1),
                    (2, 3, 1)]

        vertex_data = self.get_data(verticies, indicies)

        tex_coord_verticies =   [
                                (0, 0), # Bottom Left
                                (1, 0), # Bottom Right
                                (1, 1), # Top Right
                                (0, 1)  # Top Left
                                ]
        tex_coord_indicies = [(3, 0, 1),
                              (2, 3, 1)]
        tex_coord_data = self.get_data(tex_coord_verticies, tex_coord_indicies)


        vertex_data = np.hstack([vertex_data, tex_coord_data])
        return vertex_data
    

class ModelVBO(BaseVBO):
    def __init__(self, ctx, path):
        self.path = path
        super().__init__(ctx)
        self.format = self.model.format
        self.attribs = self.model.attribs
        self.triangles = None
        self.unique_points = None

    def get_vbo(self):
        """
        Creates a buffer with the vertex data
        """
        
        self.vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(self.vertex_data)

        return vbo

    def get_vertex_data(self):
        self.model = load_model(self.path)
        return self.model.vertex_data