from marching_cubes_chunk import Chunk, CHUNK_SIZE
import numpy as np
import glm
from voxel_marching_cubes_construct import add_voxel_model
from numba import njit
import moderngl as mgl

import sys

#np.set_printoptions(threshold=sys.maxsize)

def get_data(chunks):
    buffer = np.vstack([chunk.VBO.vertex_data for chunk in chunks], dtype='f4')
    vert = np.array(buffer[:,3:6], dtype='f4')
    vert = vert.reshape((vert.shape[0]//3, 9))
    inst = np.array(buffer[:,np.r_[0:3,6:9]][::3], dtype='f4')
    data = np.hstack((vert, inst))
    return data

class ChunkHandler():
    
    def __init__(self, scene):
        self.scene = scene
        self.chunks = {}

        self.update_chunks = []

        self.world_size = 24

        self.programs = self.scene.vao_handler.program_handler.programs

        for x in range(self.world_size):
            for y in range(3):
                for z in range(self.world_size):
                    self.chunks[f'{x};{y};{z}'] = (Chunk(self.scene.ctx, self.chunks, self.programs, self.scene, (x, y, z)))
        
        add_voxel_model(self.chunks, 'car', (10, 4, 10))

        for chunk in list(self.chunks.values()):
            chunk.generate_mesh()

        self.instance_buffer_data = get_data(list(self.chunks.values()))
        self.depth_instance_buffer_data = np.array(self.instance_buffer_data[:,0:9], order='C')

        self.instance_buffer = self.scene.ctx.buffer(reserve=(18 * 3) * (10 ** 3) * (self.world_size ** 2 * 3))
        self.depth_instance_buffer = self.scene.ctx.buffer(reserve=(9 * 3) * (11 ** 3) * (self.world_size ** 2 * 3))

        self.triangle_vbo = self.scene.ctx.buffer(np.array([[0, 1, 2]], dtype='int'))
        
        self.vao = self.scene.ctx.vertex_array(self.programs['mesh'], [(self.triangle_vbo, '1i', 'id'), 
                                                                      (self.instance_buffer, '3f 3f 3f 3f 3f /i', 'in_i_pos0', 'in_i_pos1', 'in_i_pos2', 'in_i_norm', 'in_i_mat')], skip_errors=True)

        self.depth_vao = self.scene.ctx.vertex_array(self.programs['mesh_depth'], [(self.triangle_vbo, '1i', 'id'), 
                                                                     (self.depth_instance_buffer, 
                                                                      '3f 3f 3f /i', 
                                                                      'in_i_pos0', 'in_i_pos1', 'in_i_pos2')], skip_errors=True)


        self.instance_buffer.write(self.instance_buffer_data)
        self.depth_instance_buffer.write(self.depth_instance_buffer_data)

    def render_instanced(self):
        self.programs['mesh']['m_proj'].write(self.scene.cam.m_proj)
        self.programs['mesh']['m_view'].write(self.scene.cam.m_view)
        self.programs['mesh']['m_view_light'].write(self.scene.light_handler.dir_light.m_view_light)

        self.vao.render(instances=(len(self.instance_buffer_data)))

    def render_depth(self):
        self.programs['mesh_depth']['m_proj'].write(self.scene.cam.m_proj)
        self.programs['mesh_depth']['m_view'].write(self.scene.cam.m_view)
        self.depth_vao.render(instances=(len(self.depth_instance_buffer_data)))
                    
    def update(self):
        if len(self.update_chunks):
            self.chunks[self.update_chunks[0]].generate_mesh()
            self.update_chunks.pop(0)

            self.instance_buffer_data = get_data(list(self.chunks.values()))
            self.depth_instance_buffer_data = np.array(self.instance_buffer_data[:,0:9], order='C')
            self.instance_buffer.write(self.instance_buffer_data)
            self.depth_instance_buffer.write(self.depth_instance_buffer_data)


    def get_close_chunks(self, obj):
        possible_chunks = set([])
        for vertex in obj.hitbox.vertices:
            possible_chunks.add(self.get_chunk_from_point(vertex))
            
        # removes none from values
        possible_chunks.discard(None)
        return list(possible_chunks)
            
    def get_chunk_from_point(self, point):
        chunk = f'{int(point[0]//CHUNK_SIZE)};{int(point[1]//CHUNK_SIZE)};{int(point[2]//CHUNK_SIZE)}'
        if chunk in self.chunks.keys(): return self.chunks[chunk]
        return None
                    
    def modify_terrain(self, magnitude):
        pos = self.ray_cast()
        width = 1
        if not pos: return
        points = [(x, y, z) for x in range(-width, width + 1) for y in range(-width, width + 1) for z in range(-width, width + 1)]
        [self.modify_point(int((pos.x + point[0])), int((pos.y + point[1])), int((pos.z + point[2])), magnitude / ((abs(point[0]) + abs(point[1]) + abs(point[2])) * .5 * width + .0001)) for point in points]

    def modify_point(self, x, y, z, magnitude, material=False):

        local_pos = [x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE]
        chunk_pos = [x // CHUNK_SIZE, y // CHUNK_SIZE, z // CHUNK_SIZE]

        chunk = f'{int(chunk_pos[0])};{int(chunk_pos[1])};{int(chunk_pos[2])}'

        if chunk not in self.chunks: return
        
        self.chunks[chunk].field[local_pos[0]][local_pos[1]][local_pos[2]] += magnitude
        if magnitude > 0:
            self.chunks[chunk].materials[local_pos[0]][local_pos[1]][local_pos[2]] = 3

        edges = [(x, y, z) for x in range(0, 1 + int(local_pos[0] == 0)) for y in range(0, 1 + int(local_pos[1] == 0)) for z in range(0, 1 + int(local_pos[2] == 0))]
        for edge in edges:
            edge_chunk_key = f'{int(chunk_pos[0]) - edge[0]};{int(chunk_pos[1]) - edge[1]};{int(chunk_pos[2]) - edge[2]}'
            if edge_chunk_key in self.update_chunks: continue
            if edge_chunk_key not in self.chunks: continue
            self.update_chunks.append(edge_chunk_key)

    def ray_cast(self):
        ray_cast_pos = None

        step_size = glm.vec3(np.cos(np.deg2rad(self.scene.cam.yaw)) * np.cos(np.deg2rad(self.scene.cam.pitch)), np.sin(np.deg2rad(self.scene.cam.pitch)), np.sin(np.deg2rad(self.scene.cam.yaw)) * np.cos(np.deg2rad(self.scene.cam.pitch))) * .5
        for i in range(150):
            pos = self.scene.cam.position + step_size * i
            cam_chunk = f'{int(pos.x // CHUNK_SIZE)};{int(pos.y // CHUNK_SIZE)};{int(pos.z // CHUNK_SIZE)}'
            if cam_chunk in self.chunks:
                if self.chunks[cam_chunk].field[int(pos.x) % CHUNK_SIZE][int(pos.y) % CHUNK_SIZE][int(pos.z) % CHUNK_SIZE] > 0:
                    ray_cast_pos = pos
                    break

        return ray_cast_pos

