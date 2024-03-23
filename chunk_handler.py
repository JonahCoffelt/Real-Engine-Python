from marching_cubes_chunk import Chunk, CHUNK_SIZE
import numpy as np
import glm

class ChunkHandler():
    
    def __init__(self, scene):
        
        self.scene = scene
        self.chunks = {}
        for x in range(12):
            for y in range(3):
                for z in range(12):
                    self.chunks[f'{x};{y};{z}'] = (Chunk(self.scene.ctx, self.scene.vao_handler.program_handler.programs, self.scene, (x, y, z)))
                    
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
            chunks = []
            for x in range(-width, width + 1):
                for y in range(-width, width + 1):
                    for z in range(-width, width + 1):
                        local_pos = [int((pos.x + x)) % CHUNK_SIZE, int((pos.y + y)) % CHUNK_SIZE, int((pos.z + z)) % CHUNK_SIZE]
                        chunk_pos = [int((pos.x + x)) // CHUNK_SIZE, int((pos.y + y)) // CHUNK_SIZE, int((pos.z + z)) // CHUNK_SIZE]

                        edge_chunks = [1, 1, 1]
                        if local_pos[0] == 0:
                            edge_chunks[0] = 2
                        if local_pos[1] == 0:
                            edge_chunks[1] = 2
                        if local_pos[2] == 0:
                            edge_chunks[2] = 2

                        for x_edge in range(edge_chunks[0]):
                            for y_edge in range(edge_chunks[1]):
                                for z_edge in range(edge_chunks[2]):
                                    local_x = local_pos[0]
                                    if x_edge: local_x = CHUNK_SIZE
                                    local_y = local_pos[1]
                                    if y_edge: local_y = CHUNK_SIZE
                                    local_z = local_pos[2]
                                    if z_edge: local_z = CHUNK_SIZE
                                    chunk = f'{int(chunk_pos[0] - x_edge)};{int(chunk_pos[1] - y_edge)};{int(chunk_pos[2] - z_edge)}'
                                    if chunk in self.chunks:
                                        if magnitude > 0:
                                            self.chunks[chunk].field[local_x][local_y][local_z] += magnitude / ((abs(x) + abs(y) + abs(z)) * .5 * width + .0001)
                                            self.chunks[chunk].materials[local_x][local_y][local_z] = 3
                                        else:
                                            self.chunks[chunk].field[local_x][local_y][local_z] += magnitude /  .5 * width + .0001
                                        self.chunks[chunk].field[local_x][local_y][local_z] = max(min(self.chunks[chunk].field[local_x][local_y][local_z], 1.0), -1.0)
                                        if chunk not in chunks:
                                            chunks.append(chunk)
            for chunk in chunks:
                self.chunks[chunk].generate_mesh()
                
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