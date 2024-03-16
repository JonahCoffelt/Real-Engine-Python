import numpy as np
import glm
import random
from marching_cubes_mesh import ChunkMeshVBO
from numba import njit
from model import BaseModel


CHUNK_SIZE = 10
SEED = random.randrange(1000)


def generate_island(field, materials, chunk_x, chunk_y, chunk_z) -> np.array:
    center = CHUNK_SIZE / 2
    world_size = CHUNK_SIZE * 6
    for local_z in range(CHUNK_SIZE + 1):
        for local_x in range(CHUNK_SIZE + 1):
            global_x, global_z = local_x + chunk_x * CHUNK_SIZE, local_z + chunk_z * CHUNK_SIZE
            
            dist = np.sqrt((world_size / 2 - global_x) ** 2 + (world_size / 2 - global_z) ** 2)
            dist /= (world_size / 2)
            if dist != 0: height = (min(1 / (dist ** 2), 5) - 3) * 5
            else : height = (min(1 / (.001 ** 2), 5) - 3) * 5

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
    def __init__(self, ctx, programs, scene, pos: tuple):
        self.ctx = ctx
        self.programs = programs
        self.scene = scene
        self.pos = pos

        self.surf_lvl = 0.0

        self.obj_type = 'meshes'
        self.program_name = 'mesh'

        self.field = np.zeros(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='f4')
        self.materials = np.zeros(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='int8')
        self.field, self.materials = generate_island(self.field, self.materials, *pos)

        self.vbo = ChunkMeshVBO(self.ctx, self.field, self.materials, self.surf_lvl)

        self.set_vaos()

    def generate_mesh(self):
        #self.destroy()

        self.vbo = ChunkMeshVBO(self.ctx, self.field, self.materials, self.surf_lvl)

        self.set_vaos()

    def render(self, vao):
        self.model.render(vao)

    def get_vao(self, program, vbo):
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        return vao

    def set_vaos(self):
        self.vaos = {}
        self.vaos['default'] = self.get_vao(program=self.programs['mesh'], 
                                         vbo=self.vbo)
        self.vaos['shadow'] = self.get_vao(program=self.programs['shadow_map'], 
                                         vbo=self.vbo)
        self.vaos['normal'] = self.get_vao(program=self.programs['buffer_normal'], 
                                         vbo=self.vbo)
        self.vaos['depth'] = self.get_vao(program=self.programs['buffer_depth'], 
                                         vbo=self.vbo)
        
        self.model = ChunkModel(self.pos, self.scene, self.vaos)

    def destroy(self):
        self.vbo.destroy()
        for vao in self.vaos.values():
            vao.release()


class ChunkModel(BaseModel):
    def __init__(self, pos, scene, vaos) -> None:
        self.pos = glm.vec3(pos) * (CHUNK_SIZE)
        self.scene = scene
        self.vaos = vaos
        self.camera = scene.graphics_engine.camera
        self.m_model = self.get_model_matrix()

        self.on_init()

    def on_init(self):
        self.programs = { 'default' : self.vaos['default'].program, 'normal' : self.vaos['normal'].program, 'depth' : self.vaos['depth'].program, 'shadow' : self.vaos['shadow'].program }
        for program in self.programs:
            self.programs[program]['m_proj'].write(self.camera.m_proj)

    def get_model_matrix(self):
        m_model = glm.mat4()
        # Translate
        m_model = glm.translate(m_model, self.pos)

        return m_model