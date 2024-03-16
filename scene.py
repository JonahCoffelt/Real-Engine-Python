from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler
from buffer_handler import BufferHandler
from entity_handler import EntityHandler, ObjectHandler
from marching_cubes_chunk import Chunk, CHUNK_SIZE
import numpy as np
import glm


class Scene:
    def __init__(self, graphics_engine) -> None:
        self.graphics_engine = graphics_engine
        self.ctx = graphics_engine.ctx
        self.cam = self.graphics_engine.camera
        self.time = 0

        self.vao_handler = VAOHandler(self.ctx)
        self.texture_handler = TextureHandler(self.graphics_engine.app)
        self.buffer_handler = BufferHandler(self)
        self.vao_handler.set_up()
        self.light_handler = LightHandler()
        self.vao_handler.program_handler.set_attribs(self)
        self.entity_handler = EntityHandler()
        self.object_handler = ObjectHandler(self)
        
        # Generate island of chunks 
        self.chunks = {}
        for x in range(6):
            for y in range(3):
                for z in range(6):
                    self.chunks[f'{x};{y};{z}'] = (Chunk(self.ctx, self.vao_handler.program_handler.programs, self, (x, y, z)))

        # Shadow map buffer
        self.shadow_texture = self.texture_handler.textures['shadow_map_texture']
        self.shadow_fbo = self.ctx.framebuffer(depth_attachment=self.shadow_texture)

        self.shadow_timer = 5
        self.shadow_frame_skips = 5

    def update(self, delta_time):
        #self.time += self.graphics_engine.app.delta_time
        #self.light_handler.dir_light.color = glm.vec3(np.array([1, 1, 1]) - np.array([.8, .9, .6]) * (min(.75, max(.25, (np.sin(self.time / 500)*.5 + .5))) * 2 - .5))
        
        self.vao_handler.program_handler.update_attribs(self)  # Updates the values sent to uniforms
        self.object_handler.update(delta_time)  # Updates the objects

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
                                    if chunk in self.graphics_engine.scene.chunks:
                                        if magnitude > 0:
                                            self.graphics_engine.scene.chunks[chunk].field[local_x][local_y][local_z] += magnitude / ((abs(x) + abs(y) + abs(z)) * .5 * width + .0001)
                                            self.graphics_engine.scene.chunks[chunk].materials[local_x][local_y][local_z] = 3
                                        else:
                                            self.graphics_engine.scene.chunks[chunk].field[local_x][local_y][local_z] += magnitude /  .5 * width + .0001
                                        self.graphics_engine.scene.chunks[chunk].field[local_x][local_y][local_z] = max(min(self.graphics_engine.scene.chunks[chunk].field[local_x][local_y][local_z], 1.0), -1.0)
                                        if chunk not in chunks:
                                            chunks.append(chunk)
            for chunk in chunks:
                self.graphics_engine.scene.chunks[chunk].generate_mesh()

    def ray_cast(self):
        ray_cast_pos = None

        # Define a standard step in the look direction
        step_size = glm.vec3(np.cos(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch)), np.sin(np.deg2rad(self.cam.pitch)), np.sin(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch))) * .5
        # Traverse forward with the step size
        for i in range(150):
            pos = self.cam.position + step_size * i
            cam_chunk = f'{int(pos.x // CHUNK_SIZE)};{int(pos.y // CHUNK_SIZE)};{int(pos.z // CHUNK_SIZE)}'
            if cam_chunk in self.chunks:
                if self.chunks[cam_chunk].field[int(pos.x) % CHUNK_SIZE][int(pos.y) % CHUNK_SIZE][int(pos.z) % CHUNK_SIZE] > 0: # Check if point is above curface level
                    ray_cast_pos = pos
                    break

        return ray_cast_pos

    def render_buffers(self):
        # Renders each of the buffers
        self.buffer_handler.buffers['frame'].use()   # Frame Buffer
        self.object_handler.render('skybox', light=False, object_types=('skybox'))
        self.object_handler.render(False, light=False, object_types=('container', 'metal_box', 'wooden_box'))
        self.object_handler.render(False, light=False, objs=self.chunks.values())
        self.buffer_handler.buffers['normal'].use()  # Normal Buffer
        self.object_handler.render('buffer_normal', 'normal', ('container', 'metal_box', 'wooden_box', 'meshes'))
        self.object_handler.render('buffer_normal', 'normal', objs=self.chunks.values())
        self.buffer_handler.buffers['depth'].use()   # Depth Buffer
        self.object_handler.render('buffer_depth', 'depth', ('container', 'metal_box', 'wooden_box', 'meshes'))
        self.object_handler.render('buffer_depth', 'depth', objs=self.chunks.values())
        self.shadow_fbo.clear() # Shadow Buffer
        self.shadow_fbo.use()
        self.object_handler.apply_shadow_shader_uniforms()
        self.object_handler.render('shadow_map', 'shadow', ('container', 'metal_box', 'wooden_box', 'meshes', 'cat'))
        self.object_handler.render('shadow_map', 'shadow', objs=self.chunks.values())

    def render_filters(self):
        sharpen_buffer = self.buffer_handler.buffers['edge_detect']
        sharpen_buffer.use()

        sharpen_buffer.vao.program['u_texture'] = 2
        self.buffer_handler.buffers['depth'].texture.use(location=2)

        sharpen_buffer.vao.render()

    def render_screen(self):
        self.ctx.screen.use()

        frame_vao = self.buffer_handler.buffers['frame'].vao
        frame_vao.program['screenTexture'] = 0
        self.buffer_handler.buffers['frame'].texture.use(location=0)
        #frame_vao.program['normalTexture'] = 1
        #self.buffer_handler.buffers['normal'].texture.use(location=1)
        #frame_vao.program['depthTexture'] = 2
        #self.buffer_handler.buffers['depth'].texture.use(location=2)
        frame_vao.program['outlineTexture'] = 4
        self.buffer_handler.buffers['edge_detect'].texture.use(location=4)

        frame_vao.render()

    def render(self, delta_time):
        self.update(delta_time)  # Updates objects, time, and uniforms
        self.render_buffers()  # Renders the standard buffers
        self.render_filters()  # Renders and filter buffers
        self.render_screen() # Renders buffers to screen