import glm
from material_handler import *


class BaseModel:
    def __init__(self, object, scene, vao) -> None:
        self.object = object
        self.scene = scene
        self.vao = self.scene.vao_handler.vaos[vao]
        self.program = self.vao.program
        self.camera = scene.graphics_engine.camera
        self.material = self.object.material
        self.m_model = self.get_model_matrix()

        self.on_init()

    def on_init(self):
        # MVP
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

    def update(self):
        #self.material.write(self.program)

        self.program['m_model'].write(self.m_model)

    def render(self):
        self.update()
        self.vao.render()

    def get_model_matrix(self):
        m_model = glm.mat4()
        # Translate
        m_model = glm.translate(m_model, self.object.pos)
        # Rotate
        m_model = glm.rotate(m_model, self.object.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.rotate(m_model, self.object.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.object.rot.z, glm.vec3(0, 0, 1))
        # Scael
        m_model = glm.scale(m_model, self.object.scale)
        return m_model