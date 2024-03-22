import model
import glm
from material_handler import MaterialHandler
from hitboxes import *
from physics_engine import PhysicsEngine
from random import randint
from scipy.spatial.transform import Rotation as R
from quaternions import *

class ObjectHandler:
    def __init__(self, scene):
        self.scene = scene
        self.ctx = scene.ctx

        self.objects = []
        self.attrib_values, self.SHADER_ATTRIBS, self.currrent_shader_uniforms = scene.vao_handler.program_handler.attrib_values, scene.vao_handler.program_handler.SHADER_ATTRIBS, scene.vao_handler.program_handler.currrent_shader_uniforms

        self.light_handler = self.scene.light_handler
        self.material_handler = MaterialHandler(self.scene.texture_handler.textures)
        
        self.pe = PhysicsEngine(-9.8, Object(self, self.scene, model.BaseModel, program_name = 'default', material='metal_box', scale=(1, 1, 1), pos=(0, 0, 0), gravity = False, immovable = True))

        self.on_init()

    def on_init(self):
        """
        Creates objects in the scene
        """
        self.objects.append(Object(self, self.scene, model.SkyBoxModel, program_name='skybox', vao='skybox', obj_type='skybox'))
        
        #for x in range(10):  
            #self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', scale=(10, .5, 10), pos = (randint(-30, 30), randint(-40, 0), randint(-30, 30)), gravity = False, immovable = True, rot = (randint(-30, 30), 0, randint(-30, 30))))
        self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', scale=(15, .5, 15), pos = (0, -2, 0), gravity = False, immovable = True))
        
        self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='container', obj_type='container', scale=(1, 1, 1), pos = (0, -2, 0), gravity = False, immovable = True))


        for i in range(0):
            self.objects.append(Object(self, self.scene, model.BaseModel, program_name='default', material='metal_box', obj_type='metal_box', pos=(randint(-10, 10), randint(0, 15), randint(-10, 10)), rot = (randint(0, 120), 0, randint(0, 120)), scale=(.5, .5, .5)))

    def update(self, delta_time):
    
        for obj in self.objects:
                
            # checks if object needs physics calculations  
            if obj.immovable: continue    
                
            # changes pos of all models in scene based off hitbox vel
            obj.move_tick(delta_time)
                
            # changes velocity based off euler steps
            force = glm.vec3(0, 0, 0)
            if obj.gravity: 
                force[1] = self.pe.gravity_strength
            obj.hitbox.move_tick(delta_time, force, 0)
                
            # tp object to top if hits death plane
            if obj.pos[1] < -60: 
                obj.set_pos(glm.vec3(randint(-20, 20), randint(10, 30), randint(-20, 20)))
                obj.hitbox.set_vel(glm.vec3(0, 0, 0))
                obj.hitbox.set_rot_axis(glm.vec3(0, 1, 0))
                obj.hitbox.set_rot_vel(0)
                
        # object - object collisions
        self.pe.resolve_collisions(self.objects, delta_time)
        self.pe.resolve_terrain_collisions(self.objects, delta_time, self.scene.chunks)

    def write_shader_uniforms(self, program_name, obj_type=None, material=None):
        """
        This is the primary method for sending unforms to the shader programs.
        See shader_program_handler.ProgramHandler.set_attribs for more info.
        """
        program = self.scene.vao_handler.program_handler.programs[program_name]
        shader_attribs = self.SHADER_ATTRIBS
        attribs = shader_attribs[program_name]
        attrib_values = self.attrib_values

        for attrib in attribs[0]:  # Writes int, float, and vector uniforms
            if attrib == 'view_pos': program[attrib].write(attrib_values[attrib])
            if attrib == 'm_view': program[attrib].write(attrib_values[attrib])
            if attrib_values[attrib] == self.currrent_shader_uniforms[program_name][attrib]: continue
            program[attrib].write(attrib_values[attrib])
            self.currrent_shader_uniforms[program_name][attrib] = attrib_values[attrib]

        for i, texture in enumerate(attribs[1]):  # Writes texture uniforms
            if attrib_values[texture] == self.currrent_shader_uniforms[program_name][texture]: continue
            program[texture] = i + 3
            attrib_values[texture].use(location = i + 3)
            self.currrent_shader_uniforms[program_name][texture] = attrib_values[texture]

        if attribs[2]['light'] and obj_type != 'skybox' and self.currrent_shader_uniforms[program_name]['light']: # Writes light uniforms
            self.light_handler.write(program)
            self.currrent_shader_uniforms[program_name]['light'] = False

        if attribs[2]['material'] and obj_type != 'skybox' and obj_type != self.currrent_shader_uniforms[program_name]['material']: # Writes material uniforms
            self.material_handler.materials[material].write(program)
            self.currrent_shader_uniforms[program_name]['material'] = material

    def apply_shadow_shader_uniforms(self):
        programs = self.scene.vao_handler.program_handler.programs
        for program in programs:
            if not (program == 'default' or program == 'mesh'): continue
            self.write_shader_uniforms('mesh')

    def render(self, program_name, render_type='default', object_types=('container', 'metal_box', 'wooden_box', 'cat', 'skybox', 'meshes'), light=False, objs=False):
        if program_name: self.write_shader_uniforms(program_name)
        if light: # Will write all light if true
            programs = self.scene.vao_handler.program_handler.programs
            for program in programs:
                if program in ('mesh', 'default'): self.light_handler.write(programs[program])
        # Choose the objects used
        if objs: objects = objs
        else: objects = self.objects
        # loop though each object 
        for obj in objects:
            if obj.obj_type not in object_types: continue
            if not program_name:
                program = obj.program_name
                # Choose the material
                if obj.obj_type in ('container', 'metal_box', 'wooden_box', 'cat'): mat = obj.material
                else: mat = obj.obj_type
                self.write_shader_uniforms(program, obj.obj_type, mat)
            obj.render(render_type)

            
    def add_object(self, object):
        self.objects.append(object)
        return object

class Object:
    def __init__(self, obj_handler, scene, model, program_name='default', vao='cube', material='container', obj_type='none', pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), hitbox_type = 'cube', hitbox_file_name = None, rot_vel = 0.001, rot_axis = (0, 0, 0), vel = (0, 0, 0), mass = 1, immovable = False, gravity = True):
        
        self.ctx = obj_handler.ctx
        self.camera = scene.graphics_engine.camera
        self.scene = scene

        self.program_name = program_name
        self.obj_type = obj_type
        self.material = material

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = glm.vec3(scale)
        self.rot_point = [0, 0, 1]
        
        # physics variables
        self.immovable = immovable
        self.gravity = gravity
        self.mass = mass if not immovable else 1e10

        self.on_init(model, vao=vao, hitbox_type=hitbox_type, hitbox_file_name=hitbox_file_name, rot_vel=rot_vel, rot_axis=rot_axis, vel=vel)


    def on_init(self, model, vao='cube', hitbox_type = 'cube', hitbox_file_name = None, rot_vel = 0, rot_axis = (0, 0, 0), vel = (0, 0, 0)):
        self.model = model(self, self.scene, vao)

        self.hitbox = None
        match hitbox_type:
            case 'cube': self.define_hitbox_cube(vel, rot_vel, rot_axis)
            case 'rectangle': self.define_hitbox_rectangle(hitbox_file_name, vel, rot_vel, rot_axis)
            case 'fitted': self.define_hitbox_fitted(hitbox_file_name, vel, rot_vel, rot_axis)
            case _: assert False, 'hitbox type is not recognized'

    def update(self):
        self.model.rot = glm.vec3([glm.radians(a) for a in self.rot])
        self.model.update()

    def render(self, vao):
        self.model.render(vao)
        
        
    def define_hitbox_cube(self, vel, rot_vel, rot_axis):
        self.hitbox = CubeHitbox(self, vel, rot_vel, rot_axis)
            
    def define_hitbox_rectangle(self, file_name, vel, rot_vel, rot_axis):
        assert file_name != None, 'hitbox needs file name to be created'
        self.hitbox = FittedHitbox(self, file_name, True, vel, rot_vel, rot_axis)
    
    def define_hitbox_fitted(self, file_name, vel, rot_vel, rot_axis):
        assert file_name != None, 'hitbox needs file name to be created'
        self.hitbox = FittedHitbox(self, file_name, False, vel, rot_vel, rot_axis)
        
    # for physics
    def move_tick(self, delta_time):
        self.pos += delta_time * self.hitbox.vel
        self.move_tick_rot(delta_time)
        #self.model.update()
        
    def move_tick_translate(self, delta_time):
        self.pos += delta_time * self.hitbox.vel
        self.model.update()
        
    def move_tick_rot(self, delta_time):
        
        p = [0] + self.rot_point
        
        theta = delta_time * self.hitbox.rot_vel
        
        q = axis_angle_to_quaternion(self.hitbox.rot_axis, theta)
        qneg = quaternion_conjugate(q)
        
        p = quaternion_multiply(q, p)
        p = quaternion_multiply(p, qneg)
        self.rot_point = p[1:]
        
        try:
            p = R.from_quat(p)
            euler_angles = glm.vec3(p.as_euler('zyx'))
        except:
            self.rot_point = [1, 0, 0]
            euler_angles = glm.vec3(0, 0, 0)
            
        self.rot = euler_angles
        self.model.update()
        
    def get_cartesian_vertices(self):
        
        return self.hitbox.vertices
    
    # setter methods
    def set_hitbox(self, hitbox): self.hitbox = hitbox
    def set_pos(self, pos): self.pos = pos
    def set_rot(self, rot): 
        self.rot = rot
        self.rot_point = R.as_quat(R.from_euler('zyx', self.rot))
    
    # modifier methods
    def move(self, vec, delta_time):
        self.pos += vec * delta_time