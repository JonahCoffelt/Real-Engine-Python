from data.config import config
from data.vao_handler import VAOHandler
from data.texture_handler import TextureHandler
from data.light_handler import LightHandler
from data.buffer_handler import BufferHandler
from data.entity_handler import EntityHandler, ObjectHandler
from data.particle_handler import ParticleHandler
from data.chunk_handler import ChunkHandler
from data.atmosphere_handler import Atmosphere
from data.ui_handler import UI_Handler
from data.sound_handler import SoundHandler
from data.load_zone import LoadZoneHandler
#import cudart


class Scene:
    def __init__(self, graphics_engine) -> None:
        self.graphics_engine = graphics_engine
        self.ctx = graphics_engine.ctx
        self.cam = self.graphics_engine.camera
        self.loading_screen = self.graphics_engine.loading_screen
        self.time = 0
        self.power = 15
        self.tick = self.loading_screen.update

    def on_init(self):
        self.tick('Loading VAO Handler')
        self.vao_handler = VAOHandler(self.ctx, self)
        self.tick('Loading Textures')
        self.texture_handler = TextureHandler(self.graphics_engine.app)
        self.tick('Loading Buffers')
        self.buffer_handler = BufferHandler(self)
        self.tick('Loading VAOs')
        self.vao_handler.set_up()
        self.tick('Loading Lighting')
        self.light_handler = LightHandler()
        self.tick('Loading Shaders')
        self.vao_handler.program_handler.set_attribs(self)
        self.tick('Initializing Chunks')
        self.chunk_handler = ChunkHandler(self)
        self.tick('Loading Objects')
        self.object_handler = ObjectHandler(self)
        self.tick('Loading Entities')
        self.entity_handler = EntityHandler(self.object_handler, self.cam)
        self.tick('Loading Particles')
        self.particle_handler = ParticleHandler(self.ctx, self.vao_handler.program_handler.programs, self.vao_handler.vbo_handler.vbos['ico'], self.cam)
        self.tick('Loading Atmosphere')
        self.atmosphere_handler = Atmosphere(self)
        self.tick('Loading UI')
        self.ui_handler = UI_Handler(self, self.ctx, self.buffer_handler.buffers['frame'].vao, self.graphics_engine.app.win_size)
        self.tick('Loading Sound')
        self.sound_handler = SoundHandler()
        self.tick('Loading Zones')
        self.load_zone_handler = LoadZoneHandler(self)
        self.tick('Loading Chunks')
        
        self.chunk_handler.after_init()
        self.tick('Loading Entites')
        self.entity_handler.entities[0].after_init()
        self.tick('Loading Hub')

        # loads in world
        self.remove_world_scene()
        self.chunk_handler.generate_spawn()
        self.load_zone_handler.move_to_active('hub')
        self.entity_handler.entities[0].reset_player()
        self.tick('Preparing to Start')

        # Shadow map buffer
        self.shadow_texture = self.texture_handler.textures['shadow_map_texture']
        self.shadow_fbo = self.ctx.framebuffer(depth_attachment=self.shadow_texture)

        self.shadow_timer = 5
        self.shadow_frame_skips = 5

    def update(self, delta_time):

        self.chunk_handler.update()
        self.vao_handler.program_handler.update_attribs(self)  # Updates the values sent to uniforms
        self.entity_handler.update(delta_time)
        self.object_handler.update(delta_time)  # Updates the objects
        self.particle_handler.update(delta_time)  # Updates particles
        self.atmosphere_handler.update(delta_time)  # Updates the sky and time
        self.light_handler.update(self.cam.position, self.vao_handler.program_handler.programs)
        self.load_zone_handler.update(delta_time) # updates particles for load zones
        self.ui_handler.update(delta_time)

    def render_buffers(self):
        self.buffer_handler.buffers['frame'].use()   # Frame Buffer
        self.atmosphere_handler.render()
        self.object_handler.render(False, light=True, object_types=('container', 'metal_box', 'wooden_box'))
        #self.object_handler.render(False, light=True, objs=self.chunk_handler.chunks.values(), prin=True)
        self.chunk_handler.render_instanced()
        self.particle_handler.render()
        self.buffer_handler.buffers['normal'].use()  # Normal Buffer
        self.object_handler.render('buffer_normal', 'normal', ('container', 'metal_box', 'wooden_box', 'meshes'))
        #self.object_handler.render('buffer_normal', 'normal', objs=self.chunk_handler.chunks.values())
        self.buffer_handler.buffers['depth'].use()   # Depth Buffer
        self.object_handler.render('buffer_depth', 'depth', ('container', 'metal_box', 'wooden_box', 'meshes'))
        self.chunk_handler.render_depth()
        #self.object_handler.render('buffer_depth', 'depth', objs=self.chunk_handler.chunks.values())
        self.shadow_fbo.clear() # Shadow Buffer
        self.shadow_fbo.use()
        self.object_handler.apply_shadow_shader_uniforms()
        self.object_handler.render('shadow_map', 'shadow', ('container', 'metal_box', 'wooden_box', 'meshes', 'cat'))
        self.chunk_handler.render_shadow()
        #self.chunk_handler.render_depth()

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
        self.ui_handler.update(delta_time)
        if config['runtime']['simulate']: self.update(delta_time)  # Updates objects, time, and uniforms
        if not config['runtime']['render']: return
        self.render_buffers()  # Renders the standard buffers
        self.render_filters()  # Renders and filter buffers
        self.render_screen() # Renders buffers to screen

    def set_camera(self, camera):
        self.cam = camera
        self.entity_handler.set_player_camera(self.cam)
        self.particle_handler.cam = self.cam

    def update_settings(self):
        self.cam.update_settings()
        self.vao_handler.program_handler.attrib_values['m_proj'] = self.cam.m_proj
        self.vao_handler.program_handler.write_uniform('m_proj')
    
    def remove_world_scene(self):
        
        # removes entites
        self.entity_handler.clear_all()
        # removes world items
        self.chunk_handler.clear_all()
        self.light_handler.clear_all()
        self.particle_handler.emitter_handler.clear_all()
        
    def enter_dungeon(self, power):
        
        self.atmosphere_handler.set_to_dungeon()
        self.sound_handler.play_playlist('dungeon')
        self.ui_handler.update_shop()
        self.remove_world_scene()
        self.chunk_handler.fill_all()
        self.chunk_handler.generate_dungeon(power)
        self.entity_handler.entities[0].reset_player()
        
    def enter_hub(self):
        
        self.atmosphere_handler.set_to_outside()
        self.sound_handler.play_playlist('hub')
        self.ui_handler.update_shop()
        self.remove_world_scene()
        self.chunk_handler.generate_spawn()
        self.load_zone_handler.move_to_active('hub')
        self.entity_handler.entities[0].reset_player()