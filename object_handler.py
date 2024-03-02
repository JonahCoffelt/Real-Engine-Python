import model
import mesh
import glm
import numpy as np
from material_handler import MaterialHandler


class ObjectHandler:
    def __init__(self, scene):
        self.scene = scene
        self.ctx = scene.ctx

        self.objects = []
        self.attrib_values, self.SHADER_ATTRIBS, self.currrent_shader_uniforms = scene.vao_handler.program_handler.attrib_values, scene.vao_handler.program_handler.SHADER_ATTRIBS, scene.vao_handler.program_handler.currrent_shader_uniforms

        self.light_handler = self.scene.light_handler
        self.material_handler = MaterialHandler(self.scene.texture_handler.textures)

        self.on_init()

    def on_init(self):

        self.objects.append(Object(self, self.scene, model.SkyBoxModel, program_name='skybox', vao='skybox', obj_type='skybox'))

        #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(-1, 10, 1), scale=(.5, .5, .5)))

        #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(-10, 10, -10), scale=(.5, .5, .5)))
        #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(-10, 10, -20), scale=(.5, .5, .5)))
        #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(-20, 10, -10), scale=(.5, .5, .5)))
        #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(-20, 10, -20), scale=(.5, .5, .5)))

        #for x in range(-25, -5, 2):
        #    for z in range(-25, -5, 2):
        #        self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='container', obj_type='container', pos=(x, 6, z), scale=(1, 1, 1)))


        #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='mesh', vao='terrain', material='metal_box', obj_type='meshes', pos=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0)))

    def update(self):...

    def write_shader_uniforms(self, program_name, obj_type=None):
        """
        This is the primary method for sending unforms to the shader programs.
        See shader_program_handler.ProgramHandler.set_attribs for more info.
        """
        program = self.scene.vao_handler.program_handler.programs[program_name]
        shader_attribs = self.SHADER_ATTRIBS
        attribs = shader_attribs[program_name]
        attrib_values = self.attrib_values
        
        for attrib in attribs[0]:
            if attrib == 'view_pos': program[attrib].write(attrib_values[attrib])
            if attrib_values[attrib] == self.currrent_shader_uniforms[program_name][attrib]: continue
            program[attrib].write(attrib_values[attrib])
            self.currrent_shader_uniforms[program_name][attrib] = attrib_values[attrib]

        for i, texture in enumerate(attribs[1]):
            if attrib_values[texture] == self.currrent_shader_uniforms[program_name][texture]: continue
            program[texture] = i + 3
            attrib_values[texture].use(location = i + 3)
            self.currrent_shader_uniforms[program_name][texture] = attrib_values[texture]

        if attribs[2]['light'] and obj_type != 'skybox' and self.currrent_shader_uniforms[program_name]['light']:
            self.light_handler.write(program)
            self.currrent_shader_uniforms[program_name]['light'] = False

        if attribs[2]['material'] and obj_type != 'skybox' and obj_type != self.currrent_shader_uniforms[program_name]['material']:
            self.material_handler.materials[obj_type].write(program)
            self.currrent_shader_uniforms[program_name]['material'] = obj_type

    def apply_shadow_shader_uniforms(self):
        programs = self.scene.vao_handler.program_handler.programs
        for program in programs:
            if not (program == 'default' or program == 'mesh'): continue
            self.write_shader_uniforms('mesh')

    def render(self, program_name, render_type='default', object_types=('container', 'metal_box', 'cat', 'skybox', 'meshes'), light=False, objs=False):
        if program_name: self.write_shader_uniforms(program_name)
        if light:
            programs = self.scene.vao_handler.program_handler.programs
            for program in programs:
                if program in ('mesh', 'default'): self.light_handler.write(programs[program])
        if objs: objects = objs
        else: objects = self.objects
        for obj in objects:
            if obj.obj_type not in object_types: continue
            if not program_name:
                program = obj.program_name
                self.write_shader_uniforms(program, obj.obj_type)
            obj.render(render_type)


class Object:
    def __init__(self, obj_handler, scene, model, program_name='default', vao='cube', material='container', obj_type='none', pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.ctx = obj_handler.ctx
        self.camera = scene.graphics_engine.camera
        self.scene = scene

        self.program_name = program_name
        self.obj_type = obj_type
        self.material = obj_handler.material_handler.materials[material] 

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale

        self.on_init(model, vao=vao)

    def on_init(self, model, vao='cube'):
        self.model = model(self, self.scene, vao)

    def update(self):
        self.model.rot = glm.vec3([glm.radians(a) for a in self.rot])
        self.model.update()

    def render(self, vao):
        self.model.render(vao)