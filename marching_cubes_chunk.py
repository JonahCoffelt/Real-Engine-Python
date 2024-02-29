import numpy as np
import glm
import random
from marching_cubes_mesh import ChunkMeshVBO
from numba import njit
from model import BaseModel

CHUNK_SIZE = 20
SEED = random.randrange(1000)


def generate_chunk(feild, chunk_x, chunk_y, chunk_z) -> np.array:
    for local_z in range(CHUNK_SIZE + 1):
        for local_y in range(CHUNK_SIZE + 1):
            for local_x in range(CHUNK_SIZE + 1):
                global_x, global_y, global_z = local_x + chunk_x * CHUNK_SIZE, local_y + chunk_y * CHUNK_SIZE, local_z + chunk_z * CHUNK_SIZE
                feild[local_x][local_y][local_z] = glm.simplex(glm.vec3(global_x + SEED, global_y + SEED, global_z + SEED) * .05) - (global_y - 10) / 10
    return feild


def generate_sphere(feild, chunk_x, chunk_y, chunk_z) -> np.array:
    center = CHUNK_SIZE / 2
    for local_z in range(CHUNK_SIZE + 1):
        for local_y in range(CHUNK_SIZE + 1):
            for local_x in range(CHUNK_SIZE + 1):
                global_x, global_y, global_z = local_x + chunk_x * CHUNK_SIZE, local_y + chunk_y * CHUNK_SIZE, local_z + chunk_z * CHUNK_SIZE
                distance = np.sqrt((local_x - center) ** 2 + (local_y - center) ** 2 + (local_z - center) ** 2) - center * .85
                distance += glm.simplex(glm.vec3(global_x + SEED, global_y + SEED, global_z + SEED) * .1) * 2
                distance += glm.simplex(glm.vec3(global_x + SEED, global_y + SEED, global_z + SEED) * .05) ** 2 * 2
                distance = min(1.0, distance)
                distance = max(-1.0, distance)
                feild[local_x][local_y][local_z] = -distance
    return feild


def generate_island(feild, chunk_x, chunk_y, chunk_z) -> np.array:
    center = CHUNK_SIZE / 2
    for local_z in range(CHUNK_SIZE + 1):
        for local_x in range(CHUNK_SIZE + 1):
            global_x, global_z = local_x + chunk_x * CHUNK_SIZE, local_z + chunk_z * CHUNK_SIZE
            
            h1 = glm.simplex(glm.vec2(global_x + SEED, global_z + SEED) * .05) * 4
            h2 = glm.simplex(glm.vec2(global_x + SEED, global_z + SEED) * .01) ** 8 * 10
            h3 = glm.simplex(glm.vec2(global_x + SEED, global_z + SEED) * .2) * .5
            h4 = glm.simplex(glm.vec2(global_x + SEED, global_z + 100 + SEED) * .005) ** 10 * 12

            for local_y in range(CHUNK_SIZE + 1):
                global_y = local_y + chunk_y * CHUNK_SIZE
                
                height = -global_y + h1 + h2 + h3 + h4 + 4
                feild[local_x][local_y][local_z] = height
                
    return feild


class Chunk:
    def __init__(self, ctx, programs, scene, pos: tuple):
        self.ctx = ctx
        self.programs = programs
        self.scene = scene
        self.pos = pos

        self.surf_lvl = 0.0

        self.obj_type = 'meshes'
        self.program_name = 'mesh'

        self.feild = np.zeros(shape=(CHUNK_SIZE + 1, CHUNK_SIZE + 1, CHUNK_SIZE + 1), dtype='f4')
        #self.feild = generate_sphere(self.feild, *pos)
        self.feild = generate_island(self.feild, *pos)

        self.VBO = ChunkMeshVBO(self.ctx, self.feild, self.surf_lvl)

        self.set_vaos()

    def generate_mesh(self):
        self.VBO = ChunkMeshVBO(self.ctx, self.feild, self.surf_lvl)

        self.set_vaos()

    def render(self, vao):
        self.model.render(vao)

    def get_vao(self, program, vbo):
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        return vao

    def set_vaos(self):
        self.vaos = {}
        self.vaos['default'] = self.get_vao(program=self.programs['mesh'], 
                                         vbo=self.VBO)
        self.vaos['shadow'] = self.get_vao(program=self.programs['shadow_map'], 
                                         vbo=self.VBO)
        self.vaos['normal'] = self.get_vao(program=self.programs['buffer_normal'], 
                                         vbo=self.VBO)
        self.vaos['depth'] = self.get_vao(program=self.programs['buffer_depth'], 
                                         vbo=self.VBO)
        
        self.model = ChunkModel(self.pos, self.scene, self.vaos)


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