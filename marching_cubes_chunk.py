import numpy as np
import glm
import random
from marching_cubes_mesh import ChunkMeshVBO
import cudart



CHUNK_SIZE = 10
SEED = random.randrange(1000)


def generate_island(field, materials, chunk_x, chunk_y, chunk_z) -> np.array:
    center = CHUNK_SIZE / 2
    world_size = CHUNK_SIZE * 16
    for local_z in range(CHUNK_SIZE + 1):
        for local_x in range(CHUNK_SIZE + 1):
            global_x, global_z = local_x + chunk_x * CHUNK_SIZE, local_z + chunk_z * CHUNK_SIZE
            
            dist = np.sqrt((world_size / 2 - global_x) ** 2 + (world_size / 2 - global_z) ** 2)
            dist /= (world_size / 2)
            height = (min(1 / (dist ** 2), 5) - 3) * 5

            height = min(height, 1)

            height += (.75 - dist) ** 3 * 35

            h1 = (np.power(glm.simplex(glm.vec2(global_x + SEED, global_z + SEED) * .03), 3) + .25) * 8
            h2 = max(np.power(glm.simplex(glm.vec2(global_x + SEED, global_z + SEED) * .03), 8) * 9 - 1.5, 0)
            h3 = np.power(glm.simplex(glm.vec2(global_x + SEED, global_z + SEED) * .1), 3) * 2

            height = max(height + h1 + h2 + h3, 0)

            for local_y in range(CHUNK_SIZE + 1):
                global_y = local_y + chunk_y * CHUNK_SIZE
                field[local_x][local_y][local_z] = max(min(height - global_y, 1.0), -1.0)

                global_y = local_y + chunk_y * CHUNK_SIZE
                mat_value = global_y + np.sin(local_x) + np.cos(local_z)
                if global_y < 1:
                    continue
                elif mat_value > 12:
                    materials[local_x][local_y][local_z] = 4
                elif mat_value > 9:
                    materials[local_x][local_y][local_z] = 3
                elif mat_value > 6:
                    materials[local_x][local_y][local_z] = 2
                else:
                    materials[local_x][local_y][local_z] = 1

    return field, materials


class Chunk:
    def __init__(self, ctx, chunks, programs, scene, pos: tuple):
        self.ctx = ctx
        self.chunks = chunks
        self.programs = programs
        self.scene = scene
        self.pos = pos

        self.surf_lvl = 0.0

        self.obj_type = 'meshes'
        self.program_name = 'mesh'

        self.field = np.zeros(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='f4')
        self.materials = np.zeros(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='int8')
        #self.field, self.materials = generate_island(self.field, self.materials, *pos)

        self.VBO = ChunkMeshVBO(self.ctx, self.chunks, self.pos, self.field, self.materials, self.surf_lvl)
        
    def clear_all(self):
        
        self.field = -1 * np.ones(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='f4')
        #self.materials = np.zeros(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='int8')
        self.generate_mesh()
        
    def fill_all(self):
        
        self.field = np.ones(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='f4')
        self.materials = np.ones(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='int8')
        self.generate_mesh()
        
    def get_close_cubes(self, obj):
        
        possible_cubes = []
        for vertex in obj.hitbox.vertices:
            possible_cubes.append(self.get_cube_from_point(vertex))
        
        return list(possible_cubes)
            
    def get_cube_from_point(self, point):
        
        x, y, z = int(point[0])%10, int(point[1])%10 , int(point[2])%10
        return self.VBO.get_single_vertex_data(x, y, z) + np.array(self.pos) * 10

    def generate_mesh(self):
        self.VBO = ChunkMeshVBO(self.ctx, self.chunks, self.pos, self.field, self.materials, self.surf_lvl, use_neighbors=True)

