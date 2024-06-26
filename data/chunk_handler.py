import numpy as np
import glm
import cudart
from data.config import config
from data.marching_cubes_chunk import Chunk, CHUNK_SIZE
from data.structure_handler import StructureHandler
from data.dungeon_generation import DungeonHandler

def get_data(chunks, pos):
    radius = config['graphics']['render_distance']
    range_chunks = [f'{x};{y};{z}' for x in range(max(int(pos[0] - radius), 0), int(pos[0] + radius)) for y in range(max(int(pos[1] - radius), 0), int(pos[1] + radius)) for z in range(max(int(pos[2] - radius), 0), int(pos[2] + radius))]
    rendered_chunks = []
    for chunk in range_chunks:
        if chunk in chunks: rendered_chunks.append(chunks[chunk])
    buffer = np.vstack([chunk.VBO.vertex_data for chunk in rendered_chunks], dtype='f4')
    vert = np.array(buffer[:,3:6], dtype='f4')
    vert = vert.reshape((vert.shape[0]//3, 9))
    inst = np.array(buffer[:,np.r_[0:3,6:9]][::3], dtype='f4')
    data = np.hstack((vert, inst))

    buffer = None
    vert = None
    inst = None
    range_chunks = None

    return data

class ChunkHandler():    
    def __init__(self, scene):
        self.scene = scene
        self.chunks = {}
        self.update_chunks = []

        self.world_size = 10
        self.world_height = 8

        self.programs = self.scene.vao_handler.program_handler.programs

        for x in range(self.world_size):
            for y in range(self.world_height):
                for z in range(self.world_size):
                    self.chunks[f'{x};{y};{z}'] = (Chunk(self.scene.ctx, self.chunks, self.programs, self.scene, (x, y, z)))

        self.chunk_pos = (self.scene.cam.position.x//10, self.scene.cam.position.y//10, self.scene.cam.position.z//10)

    def after_init(self):
        self.scene.tick('Loading Structures')
        self.structure_handler = StructureHandler(self, self.scene.light_handler, self.scene.particle_handler.emitter_handler)
        self.scene.tick('Loading Dungeon Systems')
        self.dungeon_handler = DungeonHandler((self.world_size-1, self.world_height-1, self.world_size-1))
        #self.scene.tick('Generating Meshes')
        #for chunk in list(self.chunks.values()):
        #    chunk.generate_mesh()

        self.scene.tick()
        self.instance_buffer_data = get_data(self.chunks, self.chunk_pos)
        self.scene.tick()
        self.depth_instance_buffer_data = np.array(self.instance_buffer_data[:,0:9], order='C')
        self.scene.tick()

        self.instance_buffer = self.scene.ctx.buffer(reserve=(18 * 3) * (10 ** 3) * (config['graphics']['render_distance'] ** 2 * 3))
        self.depth_instance_buffer = self.scene.ctx.buffer(reserve=(9 * 3) * (11 ** 3) * (config['graphics']['render_distance'] ** 2 * 3))

        self.triangle_vbo = self.scene.ctx.buffer(np.array([[0, 1, 2]], dtype='int'))
        
        self.vao = self.scene.ctx.vertex_array(self.programs['mesh'], [(self.triangle_vbo, '1i', 'id'), 
                                                                      (self.instance_buffer, '3f 3f 3f 3f 3f /i', 'in_i_pos0', 'in_i_pos1', 'in_i_pos2', 'in_i_norm', 'in_i_mat')], skip_errors=True)

        self.depth_vao = self.scene.ctx.vertex_array(self.programs['mesh_depth'], [(self.triangle_vbo, '1i', 'id'), 
                                                                     (self.depth_instance_buffer, 
                                                                      '3f 3f 3f /i', 
                                                                      'in_i_pos0', 'in_i_pos1', 'in_i_pos2')], skip_errors=True)
        
        self.shadow_vao = self.scene.ctx.vertex_array(self.programs['mesh_shadow'], [(self.triangle_vbo, '1i', 'id'), 
                                                                     (self.depth_instance_buffer, 
                                                                      '3f 3f 3f /i', 
                                                                      'in_i_pos0', 'in_i_pos1', 'in_i_pos2')], skip_errors=True)

        self.scene.tick()
        self.instance_buffer.write(self.instance_buffer_data)
        self.depth_instance_buffer.write(self.depth_instance_buffer_data)
        
    def clear_all(self):
        self.scene.tick('Clearing Chunks')
        for chunk in self.chunks.values():
            chunk.clear_all()
        self.scene.tick('Generating Meshes')
        for chunk in self.chunks.values():
            chunk.generate_mesh()
        self.scene.tick()

            
    def fill_all(self):
        self.scene.tick('Filling Chunks')
        for chunk in self.chunks.values():
            chunk.fill_all()
        self.scene.tick('Generating Meshes')
        for chunk in self.chunks.values():
            chunk.generate_mesh()
        
    def generate_dungeon(self, power = 15):
        self.scene.tick('Resetting Dungeon')
        self.dungeon_handler.reset((self.world_size-1, self.world_height-1, self.world_size-1))
        self.scene.tick('Generating Dungeon')
        self.dungeon_handler.generate_dungeon()
        self.scene.tick('Updating Chunks')
        updated_chunks = []

        self.scene.tick()
        for pos, room in self.dungeon_handler.room_spawns.items():
            updated_chunks += self.structure_handler.add_structure(room.file_name, [i * 10 + 10 for i in pos])

        self.scene.tick('Generating Meshes')
        for chunk in updated_chunks:
            chunk.generate_mesh()
    
        self.scene.tick('Spawning Entites')
        self.scene.entity_handler.spawn_enemies_in_dungeon(power)
        
    def generate_spawn(self):
        
        updated_chunks = self.structure_handler.add_structure('hub', (5, 5, 5))
        self.scene.entity_handler.build_spawn()
        for chunk in updated_chunks:
            chunk.generate_mesh()
    def render_instanced(self):
        self.programs['mesh']['m_proj'].write(self.scene.cam.m_proj)
        self.programs['mesh']['m_view'].write(self.scene.cam.m_view)
        self.programs['mesh']['m_view_light'].write(self.scene.light_handler.dir_light.m_view_light)

        self.vao.render(instances=(len(self.instance_buffer_data)))

    def render_depth(self):
        self.programs['mesh_depth']['m_proj'].write(self.scene.cam.m_proj)
        self.programs['mesh_depth']['m_view'].write(self.scene.cam.m_view)
        self.depth_vao.render(instances=(len(self.depth_instance_buffer_data)))

    def render_shadow(self):
        self.programs['mesh_shadow']['m_proj'].write(self.scene.cam.m_proj)
        self.programs['mesh_shadow']['m_view_light'].write(self.scene.light_handler.dir_light.m_view_light)
        self.shadow_vao.render(instances=(len(self.depth_instance_buffer_data)))
                    
    def update(self):
        if len(self.update_chunks):
            self.chunks[self.update_chunks[0]].generate_mesh()
            self.update_chunks.pop(0)
            if not len(self.update_chunks):
                self.instance_buffer_data = None
                self.depth_instance_buffer_data = None
                self.instance_buffer_data = get_data(self.chunks, (self.scene.cam.position.x//10, self.scene.cam.position.y//10, self.scene.cam.position.z//10))
                self.depth_instance_buffer_data = np.array(self.instance_buffer_data[:,0:9], order='C')
                self.instance_buffer.write(self.instance_buffer_data)
                self.depth_instance_buffer.write(self.depth_instance_buffer_data)

        current_pos = (self.scene.cam.position.x//10, self.scene.cam.position.y//10, self.scene.cam.position.z//10)
        if self.chunk_pos != current_pos:
            self.chunk_pos = current_pos
            self.instance_buffer_data = None
            self.depth_instance_buffer_data = None
            self.instance_buffer_data = get_data(self.chunks, (self.scene.cam.position.x//10, self.scene.cam.position.y//10, self.scene.cam.position.z//10))
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
                    
    def modify_terrain(self, magnitude, pos = None, material = 3, width = 1):
        # ray casts from the camera if position is set to none
        if pos is None: pos = self.ray_cast()
        if pos is None: return
        points = [(x/4, y/4, z/4) for x in range(-width * 4, width * 4 + 1) for y in range(-width * 4, width * 4 + 1) for z in range(-width * 4, width * 4 + 1)]
        [self.modify_point(round((pos[0] + point[0])), round((pos[1] + point[1])), round((pos[2] + point[2])), magnitude / 64 / ((abs(point[0]) + abs(point[1]) + abs(point[2])) * .5 * width + .0001), material) for point in points]

    def modify_point(self, x, y, z, magnitude, material=3):
        local_pos = [x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE]
        chunk_pos = [x // CHUNK_SIZE, y // CHUNK_SIZE, z // CHUNK_SIZE]

        chunk = f'{int(chunk_pos[0])};{int(chunk_pos[1])};{int(chunk_pos[2])}'

        if chunk not in self.chunks: return
        
        self.chunks[chunk].field[local_pos[0]][local_pos[1]][local_pos[2]] += magnitude
        if magnitude > 0:
            self.chunks[chunk].materials[local_pos[0]][local_pos[1]][local_pos[2]] = material

        edges = [(x, y, z) for x in range(0, 1 + int(local_pos[0] == 0)) for y in range(0, 1 + int(local_pos[1] == 0)) for z in range(0, 1 + int(local_pos[2] == 0))]
        for edge in edges:
            edge_chunk_key = f'{int(chunk_pos[0]) - edge[0]};{int(chunk_pos[1]) - edge[1]};{int(chunk_pos[2]) - edge[2]}'
            if edge_chunk_key in self.update_chunks: continue
            if edge_chunk_key not in self.chunks: continue
            self.update_chunks.append(edge_chunk_key)

    def set_point(self, x, y, z, value, material=False):

        local_pos = [x % CHUNK_SIZE, y % CHUNK_SIZE, z % CHUNK_SIZE]
        chunk_pos = [x // CHUNK_SIZE, y // CHUNK_SIZE, z // CHUNK_SIZE]

        chunk = f'{int(chunk_pos[0])};{int(chunk_pos[1])};{int(chunk_pos[2])}'

        if chunk not in self.chunks: return
        
        self.chunks[chunk].field[local_pos[0]][local_pos[1]][local_pos[2]] = value
        self.chunks[chunk].materials[local_pos[0] - 1][local_pos[1] - 1][local_pos[2] - 1] = material
        self.chunks[chunk].materials[local_pos[0]][local_pos[1]][local_pos[2]] = material

        edges = [(x, y, z) for x in range(0, 1 + int(local_pos[0] == 0)) for y in range(0, 1 + int(local_pos[1] == 0)) for z in range(0, 1 + int(local_pos[2] == 0))]
        for edge in edges:
            edge_chunk_key = f'{int(chunk_pos[0]) - edge[0]};{int(chunk_pos[1]) - edge[1]};{int(chunk_pos[2]) - edge[2]}'
            if edge_chunk_key in self.update_chunks: continue
            if edge_chunk_key not in self.chunks: continue
            self.update_chunks.append(edge_chunk_key)


    def ray_cast(self, tests = 150, multiplier = 0.5, position = None, test_start = 0):
        ray_cast_pos = None
        if position is None: position = self.scene.cam.position

        step_size = glm.vec3(np.cos(np.deg2rad(self.scene.cam.yaw)) * np.cos(np.deg2rad(self.scene.cam.pitch)), np.sin(np.deg2rad(self.scene.cam.pitch)), np.sin(np.deg2rad(self.scene.cam.yaw)) * np.cos(np.deg2rad(self.scene.cam.pitch))) * multiplier
        for i in range(test_start, tests):
            pos = position + step_size * i
            cam_chunk = f'{int(pos.x // CHUNK_SIZE)};{int(pos.y // CHUNK_SIZE)};{int(pos.z // CHUNK_SIZE)}'
            if cam_chunk in self.chunks:
                if self.chunks[cam_chunk].field[int(pos.x) % CHUNK_SIZE][int(pos.y) % CHUNK_SIZE][int(pos.z) % CHUNK_SIZE] > 0:
                    ray_cast_pos = pos
                    break
        return ray_cast_pos
    
    def ray_cast_vec(self, origin, vec, tests = 100, multiplier = 1, starting_test = 0):
        ray_cast_pos = None

        step_size = vec
        for i in range(starting_test, tests):
            pos = origin + step_size * i * multiplier
            cam_chunk = f'{int(pos.x // CHUNK_SIZE)};{int(pos.y // CHUNK_SIZE)};{int(pos.z // CHUNK_SIZE)}'
            if cam_chunk in self.chunks:
                if self.chunks[cam_chunk].field[int(pos.x) % CHUNK_SIZE][int(pos.y) % CHUNK_SIZE][int(pos.z) % CHUNK_SIZE] > -0.2:
                    ray_cast_pos = pos
                    break
        return ray_cast_pos