import numpy as np
import pywavefront
from mesh import *


class VBOHandler:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbos = {}
        self.vbos['cube'] = CubeVBO(self.ctx)
        self.vbos['quad'] = QuadVBO(self.ctx)
        self.vbos['cat'] = ModelVBO(self.ctx, 'objects/cat/20430_Cat_v1_NEW.obj')
        self.vbos['ico'] = ModelVBO(self.ctx, 'objects/ico/ico.obj')
        self.vbos['skybox'] = AdvancedSkyBoxVBO(self.ctx)
        self.vbos['frame'] = FrameVBO(self.ctx)

    def desstroy(self):
        [vbo.vbo.release() for vbo in self.vbos.values()]


class BaseVBO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format: str = None
        self.attrib: list = None

    def get_vertex_data(self): ...

    @staticmethod
    def get_data(verticies, indicies):
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    

class CubeVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

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

        vertex_data = np.hstack([normals, vertex_data])
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data
    

class FrameVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '2f 3f'
        self.attribs = ['in_texcoord_0', 'in_position']

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


        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data


class SkyBoxVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']

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
        vertex_data = np.flip(vertex_data, 1).copy(order='C')
        
        return vertex_data
    

class AdvancedSkyBoxVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f'
        self.attribs = ['in_position']

    def get_vertex_data(self):
        z = 0.999
        verticies = [(-1, -1, z), ( 1, 1,  z), (-1,  1, z),
                     (-1, -1, z), ( 1, -1, z), ( 1,  1, z),]

        vertex_data = np.array(verticies, dtype='f4')   
        
        return vertex_data



class ModelVBO(BaseVBO):
    def __init__(self, ctx, path):
        self.path = path
        super().__init__(ctx)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']

    def get_vertex_data(self):
        objs = pywavefront.Wavefront(self.path, cache=True, parse=True)
        obj = objs.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data