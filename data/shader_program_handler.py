import glm
import cudart


PROGRAMS = {
    'default' : 'default',
    'mesh' : 'mesh',
    'mesh_depth' : 'mesh_depth',
    'mesh_shadow' : 'mesh_shadow',
    'skybox' : 'skybox',
    'shadow_map' : 'shadow_map',
    'particle' : 'particle',
    'particle3d' : 'particle3d'
}

class ProgramHandler:
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = {}

        for program in PROGRAMS: self.programs[program] = self.get_program(PROGRAMS[program])

    def get_program(self, name):
        with open(f'shaders/{name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def destroy(self):
        [program.release() for program in self.programs]

    def update_attribs(self, scene):
        """
        Updates the unifrom attribute values in self.attrib_values.
        Only updates values which are expected to change most frames.
        """
        self.attrib_values['m_view'] = scene.cam.m_view
        self.attrib_values['view_pos'] = scene.cam.position
        self.attrib_values['m_view_sky'] = glm.mat4(glm.mat3(scene.cam.m_view))
        self.attrib_values['pitch'] = glm.float32(scene.cam.pitch)
        self.attrib_values['yaw'] = glm.float32(scene.cam.yaw)

    def write_uniform(self, uniform):
        for program in PROGRAMS:
            if uniform in self.SHADER_ATTRIBS[program][0]: self.programs[program][uniform].write(self.attrib_values[uniform])

    def set_attribs(self, scene):
        """
        Sets the attributes which will be sent to the shader uniforms.
            self.attrib_values
                Contains the values associated with all unifrom variables.
            self.SHADER_ATTRIBS
                Maps the uniform variables and textures to attribute values.
                Contains data determining if light or material is used in the shader
            self.currrent_shader_uniforms
                Contains the values in each shader programs uniforms. 
                When a uniform is sent to the shader, the value is updated here too.
                You can think of it like a grid of shader programs and unifrom variables where the cells are the current values.
                This prevents writing data which is alread there. This is a massive speed increase.
        """
        self.attrib_values = {
            'view_pos' : scene.cam.position,
            'm_view_light' : scene.light_handler.dir_light.m_view_light,
            'm_view' : scene.cam.m_view,
            'm_view_sky' : glm.mat4(glm.mat3(scene.cam.m_view)),
            'u_resolution' : glm.vec2(scene.graphics_engine.app.win_size),
            'm_proj' : scene.cam.m_proj,
            'pitch' : glm.float32(scene.cam.pitch),
            'yaw' : glm.float32(scene.cam.pitch),

            'shadowMap' : scene.texture_handler.textures['shadow_map_texture'],
            'u_texture_skybox' : scene.texture_handler.textures['skybox']
        }

        self.SHADER_ATTRIBS = {
            'default' : [
                ['view_pos', 'm_view_light', 'u_resolution', 'm_view', 'm_proj'],  # Variables
                ['shadowMap'],  # Textures
                {'light' : True, 'material' : True}  # Components
            ],
            'mesh' : [
                ['view_pos', 'm_view_light', 'u_resolution', 'm_view', 'm_proj'],  # Variables
                ['shadowMap'],  # Textures
                {'light' : True, 'material' : False}  # Components
            ],
            'skybox' : [
                ['pitch', 'yaw'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'shadow_map' : [
                ['m_view_light', 'm_proj'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'buffer_normal' : [
                ['m_view', 'm_proj'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'buffer_depth' : [
                ['m_view', 'm_proj'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'mesh_depth' : [
                ['m_proj', 'm_view', 'm_view_light'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'mesh_shadow' : [
                ['m_proj', 'm_view'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'particle' : [
                ['m_view', 'm_proj'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ],
            'particle3d' : [
                ['m_view', 'm_proj'],  # Variables
                [],  # Textures
                {'light' : False, 'material' : False}  # Components
            ]
        }

        self.currrent_shader_uniforms = {}
        for program in self.programs: 
            self.currrent_shader_uniforms[program] = {attrib : None for attrib in self.attrib_values}
            self.currrent_shader_uniforms[program]['m_view'] = scene.cam.m_view
            self.currrent_shader_uniforms[program]['view_pos'] = scene.cam.position
            self.currrent_shader_uniforms[program]['light'] = True
            self.currrent_shader_uniforms[program]['material'] = 'asd'