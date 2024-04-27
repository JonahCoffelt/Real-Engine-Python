import glm
from data.material_handler import *
#import cudart


class BaseModel:
    def __init__(self, object, scene, vao) -> None:
        self.object = object
        self.scene = scene
        self.vao_name = vao
        self.vao = self.scene.vao_handler.vaos[vao]
        self.program = self.vao.program
        self.camera = scene.graphics_engine.camera
        self.m_model = self.get_model_matrix()

        self.on_init()

    def on_init(self, proj=True):
        # Shadow
        shadow_vao = self.scene.vao_handler.vaos[f'shadow_{self.vao_name}']
        shadow_program = shadow_vao.program
        shadow_program['m_proj'].write(self.camera.m_proj)
        # Normal
        normal_vao = self.scene.vao_handler.vaos[f'normal_{self.vao_name}']
        normal_program = normal_vao.program
        normal_program['m_proj'].write(self.camera.m_proj)
        # Depth
        depth_vao = self.scene.vao_handler.vaos[f'depth_{self.vao_name}']
        depth_program = depth_vao.program
        depth_program['m_proj'].write(self.camera.m_proj)
        # MVP
        self.program['m_proj'].write(self.camera.m_proj)

        self.vaos = { 'default' : self.vao, 'normal' : normal_vao, 'depth' : depth_vao, 'shadow' : shadow_vao }
        self.programs = { 'default' : self.program, 'normal' : normal_program, 'depth' : depth_program, 'shadow' : shadow_program }

    def update(self):
        self.m_model = self.get_model_matrix()
        self.object.hitbox.update_vertices()

    def render(self, vao):
        self.programs[vao]['m_model'].write(self.m_model)
        self.vaos[vao].render()

    def get_model_matrix(self):
        m_model = glm.mat4()
        # Translate
        m_model = glm.translate(m_model, self.object.pos)
        # Rotate
        m_model = glm.rotate(m_model, self.object.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.rotate(m_model, self.object.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.object.rot.z, glm.vec3(0, 0, 1))
        # Scale
        m_model = glm.scale(m_model, self.object.scale)
        return m_model
    

class SkyBoxModel(BaseModel):
    def __init__(self, object, scene, vao):
        self.object = object
        self.scene = scene
        self.vao_name = vao
        self.vao = self.scene.vao_handler.vaos[vao]
        self.program = self.vao.program
        self.m_model = self.get_model_matrix()
        self.vaos = { 'default' : self.vao}
        self.programs = { 'default' : self.program}
        
    def on_init(self):
        # MVP
        self.program['m_proj'].write(self.camera.m_proj)

    def render(self, vao):
        self.update()
        self.vao.render()