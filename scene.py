from object_handler import ObjectHandler
from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler
from buffer_handler import BufferHandler
from marching_cubes_chunk import Chunk
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
        self.objects = ObjectHandler(self)
        
        self.chunks = []
        for x in range(4):
            for z in range(4):
                self.chunks.append(Chunk(self.ctx, self.vao_handler.program_handler.programs, self, (x, 0, z)))

        # Shadow map buffer
        self.shadow_texture = self.texture_handler.textures['shadow_map_texture']
        self.shadow_fbo = self.ctx.framebuffer(depth_attachment=self.shadow_texture)

        self.shadow_timer = 5
        self.shadow_frame_skips = 5

    def update(self):
        #self.time += self.graphics_engine.app.delta_time
        self.light_handler.dir_light.color = glm.vec3(np.array([1, 1, 1]) - np.array([.8, .9, .6]) * (min(.75, max(.25, (np.sin(self.time / 500)*.5 + .5))) * 2 - .5))
        
        self.vao_handler.program_handler.update_attribs(self)  # Updates the values sent to uniforms
        self.objects.update()  # Updates the objects

    def render_buffers(self):
        self.buffer_handler.buffers['frame'].use()   # Frame Buffer
        self.objects.render(False, light=True)
        self.objects.render(False, light=True, objs=self.chunks)
        self.buffer_handler.buffers['normal'].use()  # Normal Buffer
        self.objects.render('buffer_normal', 'normal', ('container', 'metal_box', 'meshes'))
        self.objects.render('buffer_normal', 'normal', objs=self.chunks)
        self.buffer_handler.buffers['depth'].use()   # Depth Buffer
        self.objects.render('buffer_depth', 'depth', ('container', 'metal_box', 'meshes'))
        self.objects.render('buffer_depth', 'depth', objs=self.chunks)
        self.shadow_fbo.clear() # Shadow Buffer
        self.shadow_fbo.use()
        self.objects.apply_shadow_shader_uniforms()
        self.objects.render('shadow_map', 'shadow', ('container', 'metal_box', 'meshes', 'cat'))
        self.objects.render('shadow_map', 'shadow', objs=self.chunks)

    def render_filters(self):
        sharpen_buffer = self.buffer_handler.buffers['edge_detect']
        sharpen_buffer.use()

        sharpen_buffer.vao.program['texture'] = 2
        self.buffer_handler.buffers['depth'].texture.use(location=2)

        sharpen_buffer.vao.render()

    def render_screen(self):
        self.ctx.screen.use()

        frame_vao = self.buffer_handler.buffers['frame'].vao
        frame_vao.program['screenTexture'] = 0
        self.buffer_handler.buffers['frame'].texture.use(location=0)
        frame_vao.program['normalTexture'] = 1
        self.buffer_handler.buffers['normal'].texture.use(location=1)
        frame_vao.program['depthTexture'] = 2
        self.buffer_handler.buffers['depth'].texture.use(location=2)
        frame_vao.program['outlineTexture'] = 4
        self.buffer_handler.buffers['edge_detect'].texture.use(location=4)

        frame_vao.render()

    def render(self):
        self.update()  # Updates objects, time, and uniforms
        self.render_buffers()  # Renders the standard buffers
        self.render_filters()  # Renders and filter buffers
        self.render_screen() # Renders buffers to screen