import numpy as np
from numba import njit

@njit
def normalized(a):
    normalized = a / np.sqrt(np.sum(a**2))
    normalized = normalized.astype('f4') 
    return normalized


def get_normals(verticies, indicies, n=3):
    normals = [normalized(np.cross(verticies[triangle[1]] - verticies[triangle[0]], verticies[triangle[2]] - verticies[triangle[0]])) for triangle in indicies for i in range(n)]
    normals = np.array(normals)
    normal_data = normals.reshape(3 * len(indicies), 3)
    return normal_data

class BaseMeshVBO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format: str = None
        self.attrib: list = None

    @staticmethod
    def get_data(verticies, indicies):
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vertex_data(self): ...

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    

class TriangleVBO(BaseMeshVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 3f'
        self.attribs = ['in_normal', 'in_position']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],
                     [ 1, -1, 0],
                     [ 0,  1, 0]])
        indicies = [(2, 0, 1)]

        vertex_data = np.array(self.get_data(verticies, indicies), dtype='f4')

        normal_data = get_normals(verticies, indicies)

        vertex_data = np.hstack([normal_data, vertex_data])
        return vertex_data


class QuadVBO(BaseMeshVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 3f'
        self.attribs = ['in_normal', 'in_position']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],  # Bottom Left
                     [ 1, -1, 0],  # Bottom Right
                     [ 1,  1, 0],   # Top Right
                     [-1,  1, 0],  # Top Left
                     ])
        indicies = [(3, 0, 1),
                    (2, 3, 1)]

        vertex_data = self.get_data(verticies, indicies)

        normal_data = get_normals(verticies, indicies)

        vertex_data = np.hstack([normal_data, vertex_data])
        return vertex_data


class PlaneVBO(BaseMeshVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 3f'
        self.attribs = ['in_normal', 'in_position']

    def get_quad(self, offset: tuple):
        verticies = np.array([[-1 + offset[0], 0,  1 + offset[1]],  # Bottom Left
                     [ 1 + offset[0], 0,  1 + offset[1]],  # Bottom Right
                     [ 1 + offset[0], 0, -1 + offset[1]],  # Top Right
                     [-1 + offset[0], 0, -1 + offset[1]],  # Top Left
                     ])
        indicies = [(3, 0, 1),
                    (2, 3, 1)]

        vertex_data = self.get_data(verticies, indicies)

        normal_data = get_normals(verticies, indicies)

        vertex_data = np.hstack([normal_data, vertex_data])
        return vertex_data

    def get_vertex_data(self):
        vertex_data = np.array(self.get_quad((0, 0)), dtype='f4')
        n = 25
        for x in range(-n, n + 1):
            for y in range(-n, n + 1):
                vertex_data = np.vstack([vertex_data, self.get_quad((x*2, y*2))])

        return vertex_data