import model
import glm
from material_handler import MaterialHandler

class ObjectHandler:
    def __init__(self, scene):
        self.app = scene.app
        self.scene = scene
        self.objects = []

        self.material_handler = MaterialHandler(self.scene.texture_handler.textures)

        self.on_init()

    def on_init(self):
        n, s = 20, 2
        for x in range(-n, n):
            for z in range(-n, n):
                self.objects.append(Object(self, self.app, self.scene, model.BaseModel, pos=(x*s, -2, z*s)))

        self.objects.append(Object(self, self.app, self.scene, model.BaseModel, pos=(1, 1, 1), scale=(.25, .25, .25), material='metal_box'))
        self.objects.append(Object(self, self.app, self.scene, model.BaseModel, pos=(-10, 1, 1), scale=(.25, .25, .25), material='metal_box'))
        self.objects.append(Object(self, self.app, self.scene, model.BaseModel, pos=(10, 1, 15), scale=(.25, .25, .25), material='metal_box'))

    def render(self):
        for obj in self.objects:
            obj.render()

class Object:
    def __init__(self, obj_handler, app, scene, model, material='container', pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.ctx = app.ctx
        self.camera = scene.graphics_engine.camera
        self.scene = scene

        self.material = obj_handler.material_handler.materials[material] 

        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale

        self.on_init(model)

    def on_init(self, model, vao='cube', texture=0):
        self.model = model(self, self.scene, vao, texture)

    def render(self):
        self.model.render()