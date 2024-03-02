import numpy as np
from numba import njit
from marching_cube_tables import edge_table, tri_table

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
    
@ njit
def vertex_interp(p1, p2, v1, v2, isolevel):
    mu = (isolevel - v1) / (v2 - v1)
    point = p1 + mu * (p2 - p1)
    return point

@ njit
def vertex_interp2(p1, p2, v1, v2, isolevel):
    return (p2 + p1) / 2

@ njit
def get_cube(feild, edge_table, tri_table, surf_lvl, x, y, z):
    pos = np.array([x, y, z], dtype='f4')
    vert_list = np.zeros(shape=(12, 3), dtype='f4')
    vals = np.zeros(shape=(8), dtype='f4')

    rel_v0 = np.array([0.0, 0.0, 0.0], dtype='f4')
    rel_v1 = np.array([1.0, 0.0, 0.0], dtype='f4')
    rel_v2 = np.array([1.0, 0.0, 1.0], dtype='f4')
    rel_v3 = np.array([0.0, 0.0, 1.0], dtype='f4')
    rel_v4 = np.array([0.0, 1.0, 0.0], dtype='f4')
    rel_v5 = np.array([1.0, 1.0, 0.0], dtype='f4')
    rel_v6 = np.array([1.0, 1.0, 1.0], dtype='f4')
    rel_v7 = np.array([0.0, 1.0, 1.0], dtype='f4')

    vals[0] = feild[x + 0][y + 0][z + 0]
    vals[1] = feild[x + 1][y + 0][z + 0]
    vals[2] = feild[x + 1][y + 0][z + 1]
    vals[3] = feild[x + 0][y + 0][z + 1]
    vals[4] = feild[x + 0][y + 1][z + 0]
    vals[5] = feild[x + 1][y + 1][z + 0]
    vals[6] = feild[x + 1][y + 1][z + 1]
    vals[7] = feild[x + 0][y + 1][z + 1]

    cube_state = 0
    for i, val in enumerate(vals):
        if val >= surf_lvl:
            cube_state += np.power(2, i)
            

    intersected_points = edge_table[cube_state]

    if intersected_points & 1:    vert_list[0] =  vertex_interp(rel_v0, rel_v1, vals[0], vals[1], surf_lvl)
    if intersected_points & 2:    vert_list[1] =  vertex_interp(rel_v1, rel_v2, vals[1], vals[2], surf_lvl)
    if intersected_points & 4:    vert_list[2] =  vertex_interp(rel_v2, rel_v3, vals[2], vals[3], surf_lvl)
    if intersected_points & 8:    vert_list[3] =  vertex_interp(rel_v3, rel_v0, vals[3], vals[0], surf_lvl)
    if intersected_points & 16:   vert_list[4] =  vertex_interp(rel_v4, rel_v5, vals[4], vals[5], surf_lvl)
    if intersected_points & 32:   vert_list[5] =  vertex_interp(rel_v5, rel_v6, vals[5], vals[6], surf_lvl)
    if intersected_points & 64:   vert_list[6] =  vertex_interp(rel_v6, rel_v7, vals[6], vals[7], surf_lvl)
    if intersected_points & 128:  vert_list[7] =  vertex_interp(rel_v7, rel_v4, vals[7], vals[4], surf_lvl)
    if intersected_points & 256:  vert_list[8] =  vertex_interp(rel_v0, rel_v4, vals[0], vals[4], surf_lvl)
    if intersected_points & 512:  vert_list[9] =  vertex_interp(rel_v1, rel_v5, vals[1], vals[5], surf_lvl)
    if intersected_points & 1024: vert_list[10] = vertex_interp(rel_v2, rel_v6, vals[2], vals[6], surf_lvl)
    if intersected_points & 2048: vert_list[11] = vertex_interp(rel_v3, rel_v7, vals[3], vals[7], surf_lvl)

    tris = tri_table[cube_state]

    num_tris = 0
    while tris[num_tris] != -1:
        num_tris += 1

    verticies = np.zeros(shape=(num_tris, 6), dtype='f4')

    for i in range(num_tris//3):
        v1 = vert_list[tris[i*3]] + pos
        v2 = vert_list[tris[i*3 + 1]] + pos
        v3 = vert_list[tris[i*3 + 2]] + pos

        norm = -np.cross((v1 - v2), (v3 - v2))

        verticies[i*3    ] = np.array([*norm, *v1], dtype='f4')
        verticies[i*3 + 1] = np.array([*norm, *v2], dtype='f4')
        verticies[i*3 + 2] = np.array([*norm, *v3], dtype='f4')

    return verticies
    

class ChunkMeshVBO(BaseMeshVBO):
    def __init__(self, ctx, feild, surf_lvl):
        self.feild = feild
        self.CHUNK_SIZE = len(self.feild)
        self.surf_lvl = surf_lvl
        super().__init__(ctx)
        self.format = '3f 3f'
        self.attribs = ['in_normal', 'in_position']

    def get_vertex_data(self):
        vertex_data = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]], dtype='f4')
        for z in range(self.CHUNK_SIZE - 1):
            for y in range(self.CHUNK_SIZE - 1):
                for x in range(self.CHUNK_SIZE - 1):
                    cube_data = get_cube(self.feild, edge_table, tri_table, self.surf_lvl, x, y, z)
                    if len(cube_data):
                        vertex_data = np.vstack([vertex_data, cube_data], dtype='f4')

        return vertex_data