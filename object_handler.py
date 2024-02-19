import model
import glm
from material_handler import MaterialHandler

class ObjectHandler:
    def __init__(self, scene):
        self.scene = scene
        self.ctx = scene.ctx
        self.objects = {'container' : [], 'metal_box' : [], 'cat' : [], 'skybox' : []}

        light_handler = self.scene.light_handler

        self.material_handler = MaterialHandler(self.scene.texture_handler.textures)

        self.on_init()

    def on_init(self):

        self.objects['skybox'].append(Object(self, self.scene, model.SkyBoxModel, vao='skybox'))

        n, s = 10, 2
        for x in range(-n, n):
            for z in range(-n, n):
                self.objects['container'].append(Object(self, self.scene, model.BaseModel, pos=(x*s, -2, z*s)))

        self.objects['metal_box'].append(Object(self, self.scene, model.BaseModel, pos=(1, 1, 1), scale=(.25, .25, .25), material='metal_box'))
        self.objects['metal_box'].append(Object(self, self.scene, model.BaseModel, pos=(-10, 1, 1), scale=(.25, .25, .25), material='metal_box'))
        self.objects['metal_box'].append(Object(self, self.scene, model.BaseModel, pos=(10, 1, 15), scale=(.25, .25, .25), material='metal_box'))

        self.objects['cat'].append(Object(self, self.scene, model.BaseModel, vao='cat', pos=(-5, 1, 10), scale=(1, 1, 1), rot=(-90, 0, 180), material='cat'))

    def render_shadows(self):
        # Render Models
        programs = self.scene.vao_handler.program_handler.programs
        programs['shadow_map']['m_view_light'].write(self.scene.light_handler.dir_light.m_view_light)
        for obj_type in self.objects:
            if obj_type != 'skybox':
                for obj in self.objects[obj_type]:
                    obj.render_shadow()
    
    def render(self):
        programs = self.scene.vao_handler.program_handler.programs
        for obj_type in self.objects:
            for program in programs:
                if obj_type in ('container', 'metal_box', 'cat') and program == 'default':
                    # Materials
                    self.material_handler.materials[obj_type].write(programs[program])
                    # Lighting
                    self.scene.light_handler.write(programs[program])
                    programs['shadow_map']['m_view_light'].write(self.scene.light_handler.dir_light.m_view_light)
                    # Basic Rendering
                    programs[program]['view_pos'].write(self.scene.graphics_engine.camera.position)
                    programs[program]['m_view'].write(self.scene.graphics_engine.camera.m_view)
                    # Depth Texture
                    depth_texture = self.scene.texture_handler.textures['depth_texture']
                    programs[program]['shadowMap'] = 1
                    depth_texture.use(location=1)
                if obj_type in ('skybox') and program == 'skybox':
                    programs[program]['m_view'].write(glm.mat4(glm.mat3(self.scene.graphics_engine.camera.m_view)))
                    programs[program]['u_texture_skybox'] = 0
                    self.scene.texture_handler.textures['skybox'].use(location=0)
            for obj in self.objects[obj_type]:
                obj.render()


class Object:
    def __init__(self, obj_handler, scene, model, vao='cube', material='container', pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.ctx = obj_handler.ctx
        self.camera = scene.graphics_engine.camera
        self.scene = scene

        self.material = obj_handler.material_handler.materials[material] 

        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale

        self.on_init(model, vao=vao)

    def on_init(self, model, vao='cube'):
        self.model = model(self, self.scene, vao)

    def render(self):
        self.model.render()
    
    def render_shadow(self):
        self.model.render_shadow()