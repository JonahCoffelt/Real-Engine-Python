import glm
import numpy as np
import random
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
    

class TerrainVBO(BaseMeshVBO):
    def __init__(self, ctx):
        self.world_size = 80
        self.oninit()
        super().__init__(ctx)
        self.format = '3f 3f'
        self.attribs = ['in_normal', 'in_position']

    def oninit(self):
        n = self.world_size
        seed = random.randrange(1000)
        self.height_map = np.zeros((n) ** 2)
        for x in range(n):
            for z in range(n):
                dist = np.sqrt((self.world_size / 2 - x) ** 2 + (self.world_size / 2 - z) ** 2)
                dist /= (self.world_size / 2)
                height = (min(1 / (dist ** 2), 5) - 3) * 5

                height = min(height, 1)

                height += (.75 - dist) ** 3 * 35

                h1 = (np.power(glm.simplex(glm.vec2(x + seed, z + seed) * .03), 3) + .25) * 8
                h2 = max(np.power(glm.simplex(glm.vec2(x + seed, z + seed) * .03), 8) * 9 - 1.5, 0)
                h3 = np.power(glm.simplex(glm.vec2(x + seed, z + seed) * .1), 3) * 2

                height = max(height + h1 + h2 + h3, 0)
                self.height_map[x + z * n] = height

    
    def get_quad(self, x, z):
        scale = 1
        v0 = ((x) * scale, self.height_map[(x) + (z + 1) * self.world_size] * scale,  (z + 1) * scale),  # Bottom Left
        v1 = ((x + 1) * scale , self.height_map[(x + 1) + (z + 1) * self.world_size] * scale,  (z + 1) * scale),  # Bottom Right
        v2 = ((x + 1) * scale, self.height_map[(x + 1) + (z) * self.world_size] * scale, (z) * scale),  # Top Right
        v3 = ((x) * scale, self.height_map[(x) + (z) * self.world_size] * scale, (z) * scale),  # Top Left

        verticies = np.array([*v0, *v1, *v2, *v3], dtype='f4')

        indicies = np.array([(3, 0, 1),
                    (2, 3, 1)])

        vertex_data = self.get_data(verticies, indicies)

        normal_data = get_normals(verticies, indicies)

        vertex_data = np.hstack([normal_data, vertex_data])

        return vertex_data, verticies, indicies

    def get_vertex_data(self):
        vert_data, verts, inds = self.get_quad(0, 0)
        vertex_data = vert_data
        self.verticies = verts
        self.indicies = inds
        n = self.world_size - 1
        for x in range(1, n):
            for z in range(1, n):
                vert_data, verts, inds = self.get_quad(x, z)
                vertex_data = np.vstack([vertex_data, vert_data])
                self.verticies = np.vstack([self.verticies, verts])
                self.indicies = np.vstack([self.indicies, inds])

        return vertex_data