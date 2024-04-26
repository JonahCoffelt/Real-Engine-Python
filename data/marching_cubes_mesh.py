import numpy as np
from numba import njit
from data.marching_cube_tables import edge_table, tri_table
from data.terrain_materials import material_IDs
import cudart


@njit (cache=True) 
def normalized(a):
    normalized = a / np.sqrt(np.sum(a**2))
    normalized = normalized.astype('f4') 
    return normalized

@ njit (cache=True) 
def vertex_interp(p1, p2, v1, v2, isolevel):
    mu = (isolevel - v1) / (v2 - v1)
    point = p1 + mu * (p2 - p1)
    return point

@ njit (cache=True) 
def get_cube(field, material, edge_table, tri_table, surf_lvl, x, y, z):
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

    vals[0] = field[x + 0][y + 0][z + 0]
    vals[1] = field[x + 1][y + 0][z + 0]
    vals[2] = field[x + 1][y + 0][z + 1]
    vals[3] = field[x + 0][y + 0][z + 1]
    vals[4] = field[x + 0][y + 1][z + 0]
    vals[5] = field[x + 1][y + 1][z + 0]
    vals[6] = field[x + 1][y + 1][z + 1]
    vals[7] = field[x + 0][y + 1][z + 1]

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

    verticies = np.zeros(shape=(num_tris, 9), dtype='f4')

    for i in range(num_tris//3):
        v1 = vert_list[tris[i*3]] + pos
        v2 = vert_list[tris[i*3 + 1]] + pos
        v3 = vert_list[tris[i*3 + 2]] + pos

        norm = -np.cross((v1 - v2), (v3 - v2))

        verticies[i*3    ] = np.array([*norm, *v1, *material], dtype='f4')
        verticies[i*3 + 1] = np.array([*norm, *v2, *material], dtype='f4')
        verticies[i*3 + 2] = np.array([*norm, *v3, *material], dtype='f4')

    return verticies
    

class ChunkMeshVBO():
    def __init__(self, ctx, chunks, pos, field, materials, surf_lvl, use_neighbors=False):
        self.ctx = ctx
        self.chunks = chunks
        self.pos = pos
        self.field = field
        self.materials = materials 
        self.CHUNK_SIZE = len(self.field)
        self.surf_lvl = surf_lvl
        self.get_vbo(use_neighbors)

    def get_vbo(self, use_neighbors=True):
        self.vertex_data = None
        self.vertex_data = self.get_vertex_data(use_neighbors) + np.array([0, 0, 0, self.pos[0]*10, self.pos[1]*10, self.pos[2]*10, 0, 0, 0])

    def get_vertex_data(self, use_neighbors=True):
        vertex_data = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(3)], dtype='f4')

        if use_neighbors:
            n = self.CHUNK_SIZE+1
            field = self.field[:,:,:]
            if f'{self.pos[0]+1};{self.pos[1]};{self.pos[2]}' in self.chunks: field[-1,:n,:n] = self.chunks[f'{self.pos[0]+1};{self.pos[1]};{self.pos[2]}'].field[0, :n, :n]
            if f'{self.pos[0]};{self.pos[1]+1};{self.pos[2]}' in self.chunks: field[:n,-1,:n] = self.chunks[f'{self.pos[0]};{self.pos[1]+1};{self.pos[2]}'].field[:n, 0, :n]
            if f'{self.pos[0]};{self.pos[1]};{self.pos[2]+1}' in self.chunks: field[:n,:n,-1] = self.chunks[f'{self.pos[0]};{self.pos[1]};{self.pos[2]+1}'].field[:n, :n, 0]
            if f'{self.pos[0]+1};{self.pos[1]+1};{self.pos[2]}' in self.chunks: field[-1,-1,:n] = self.chunks[f'{self.pos[0]+1};{self.pos[1]+1};{self.pos[2]}'].field[0, 0, :n]
            if f'{self.pos[0]};{self.pos[1]+1};{self.pos[2]+1}' in self.chunks: field[:n,-1,-1] = self.chunks[f'{self.pos[0]};{self.pos[1]+1};{self.pos[2]+1}'].field[:n, 0, 0]
            if f'{self.pos[0]+1};{self.pos[1]};{self.pos[2]+1}' in self.chunks: field[-1,:n,-1] = self.chunks[f'{self.pos[0]+1};{self.pos[1]};{self.pos[2]+1}'].field[0, :n, 0]
            #if f'{self.pos[0]+1};{self.pos[1]+1};{self.pos[2]+1}' in self.chunks: field[-1,:-1,-1] = self.chunks[f'{self.pos[0]+1};{self.pos[1]+1};{self.pos[2]+1}'].field[0, 0, 0]
        else:
            field = self.field


        for z in range(self.CHUNK_SIZE - 1):
            for y in range(self.CHUNK_SIZE - 1):
                for x in range(self.CHUNK_SIZE - 1):
                    material = material_IDs[self.materials[x][y][z]]
                    cube_data = get_cube(field, material, edge_table, tri_table, self.surf_lvl, x, y, z)
                    if len(cube_data):
                        vertex_data = np.vstack([vertex_data, cube_data], dtype='f4')

        self.positions = vertex_data[:,3:6]
        self.positions = self.positions.reshape((len(self.positions)//3, 3, 3))
        norms = vertex_data[:,:3]
        self.norms = np.array([norms[i] for i in range(0, len(norms), 3)])

        return vertex_data
    
    def get_single_vertex_data(self, x, y, z):
        cube_data = get_cube(self.field, np.array([0, 0, 0]), edge_table, tri_table, self.surf_lvl, x, y, z)[:,3:6]
        cube_data = cube_data.reshape((len(cube_data)//3, 3, 3))
        
        return cube_data
    
    def release(self):
        self.ctx = None
        self.chunks = None
        self.pos = None
        self.vertex_data = None
        self.field = None
        self.materials = None
        self.chunks = None