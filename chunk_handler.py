from marching_cubes_chunk import Chunk, CHUNK_SIZE
import numpy as np
import glm
from voxel_marching_cubes_construct import add_voxel_model


class ChunkHandler():
    
    def __init__(self, scene):
        self.scene = scene
        self.chunks = {}

        self.update_chunks = []

        for x in range(12):
            for y in range(3):
                for z in range(12):
                    self.chunks[f'{x};{y};{z}'] = (Chunk(self.scene.ctx, self.chunks, self.scene.vao_handler.program_handler.programs, self.scene, (x, y, z)))
        
        add_voxel_model(self.chunks, 'car', (15, 10, 15))

        for chunk in list(self.chunks.values()):
            chunk.generate_mesh()

        
                    
    def update(self):
        if len(self.update_chunks):
            self.chunks[self.update_chunks[0]].generate_mesh()
            self.update_chunks.pop(0)

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
        if pos:
            for x in range(-width, width + 1):
                for y in range(-width, width + 1):
                    for z in range(-width, width + 1):
                        local_pos = [int((pos.x + x)) % CHUNK_SIZE, int((pos.y + y)) % CHUNK_SIZE, int((pos.z + z)) % CHUNK_SIZE]
                        chunk_pos = [int((pos.x + x)) // CHUNK_SIZE, int((pos.y + y)) // CHUNK_SIZE, int((pos.z + z)) // CHUNK_SIZE]

                        chunk = f'{int(chunk_pos[0])};{int(chunk_pos[1])};{int(chunk_pos[2])}'

                        self.chunks[chunk].field[local_pos[0]][local_pos[1]][local_pos[2]] += magnitude / ((abs(x) + abs(y) + abs(z)) * .5 * width + .0001)
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