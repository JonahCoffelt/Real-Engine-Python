from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler
from buffer_handler import BufferHandler
from entity_handler import EntityHandler, ObjectHandler
from particle_handler import ParticleHandler
from chunk_handler import ChunkHandler
import numpy as np
import glm
import moderngl as mgl
import random


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
        self.chunk_handler = ChunkHandler(self)
        self.object_handler = ObjectHandler(self)
        self.entity_handler = EntityHandler(self.object_handler, self.cam)
        self.particle_handler = ParticleHandler(self.ctx, self.vao_handler.program_handler.programs, self.vao_handler.vbo_handler.vbos['ico'], self.cam)

        # Shadow map buffer
        self.shadow_texture = self.texture_handler.textures['shadow_map_texture']
        self.shadow_fbo = self.ctx.framebuffer(depth_attachment=self.shadow_texture)

        self.shadow_timer = 5
        self.shadow_frame_skips = 5

    def update(self, delta_time):
        #self.time += self.graphics_engine.app.delta_time

        # for fire
        self.particle_handler.add_fire(pos = (random.uniform(-1, 1), random.uniform(1.5, 2.5), random.uniform(-1, 1)))

        self.light_handler.dir_light.color = glm.vec3(np.array([1, 1, 1]) - np.array([.8, .9, .6]) * (min(.75, max(.25, (np.sin(self.time / 500)*.5 + .5))) * 2 - .5))
        
        self.vao_handler.program_handler.update_attribs(self)  # Updates the values sent to uniforms
        self.entity_handler.update(delta_time)
        self.object_handler.update(delta_time)  # Updates the objects
        self.particle_handler.update(delta_time)  # Updates particles
        self.chunk_handler.update()

    def render_buffers(self):
        self.buffer_handler.buffers['frame'].use()   # Frame Buffer
        self.object_handler.render('skybox', light=False, object_types=('skybox'))
        self.object_handler.render(False, light=True, object_types=('container', 'metal_box', 'wooden_box'))
        self.object_handler.render(False, light=True, objs=self.chunk_handler.chunks.values())
        self.particle_handler.render()
        self.buffer_handler.buffers['normal'].use()  # Normal Buffer
        self.object_handler.render('buffer_normal', 'normal', ('container', 'metal_box', 'wooden_box', 'meshes'))
        self.object_handler.render('buffer_normal', 'normal', objs=self.chunk_handler.chunks.values())
        self.buffer_handler.buffers['depth'].use()   # Depth Buffer
        self.object_handler.render('buffer_depth', 'depth', ('container', 'metal_box', 'wooden_box', 'meshes'))
        self.object_handler.render('buffer_depth', 'depth', objs=self.chunk_handler.chunks.values())
        self.shadow_fbo.clear() # Shadow Buffer
        self.shadow_fbo.use()
        self.object_handler.apply_shadow_shader_uniforms()
        self.object_handler.render('shadow_map', 'shadow', ('container', 'metal_box', 'wooden_box', 'meshes', 'cat'))
        self.object_handler.render('shadow_map', 'shadow', objs=self.chunk_handler.chunks.values())

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

    def set_camera(self, camera):
        self.cam = camera
        self.entity_handler.set_player_camera(self.cam)
        self.particle_handler.cam = self.cam