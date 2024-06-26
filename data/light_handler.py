import glm
import numpy as np
from numba import njit
from data.config import config
#import cudart

@njit
def distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2))

class LightHandler:
    def __init__(self):
        self.dir_light = DirectionalLight()
        self.point_lights = []
        self.rendered_lights = []

    def update(self, pos, progs):
        pos = np.array([pos.x, pos.y, pos.z])
        self.rendered_lights = []
        for light in self.point_lights:
            if distance(light.np_pos, pos) < config['graphics']['light_range']: self.rendered_lights.append(light)
        self.write(progs['default'], dir=False)
        self.write(progs['mesh'], dir=False)
            

    def add_light(self, pos=(0, 0, 0), color=(1.0, 1.0, 1.0), brightness=1.0):
        self.point_lights.append(PointLight(pos=pos, color=color, diffuse=brightness))

    def write(self, program, dir=True, point=True):
        program['numLights'].write(glm.int32(min(len(self.rendered_lights), 99)))
        if dir:
            program['dir_light.direction'].write(self.dir_light.dir)
            program['dir_light.color'].write(self.dir_light.color)
            program['dir_light.a'].write(self.dir_light.a)
            program['dir_light.d'].write(self.dir_light.d)
            program['dir_light.s'].write(self.dir_light.s)
        if point:
            for i, light in enumerate(self.rendered_lights):
                if i > 99: continue
                program[f'pointLights[{i}].pos'].write(light.pos)
                program[f'pointLights[{i}].constant'].write(light.constant)
                program[f'pointLights[{i}].linear'].write(light.linear)
                program[f'pointLights[{i}].quadratic'].write(light.quadratic)
                program[f'pointLights[{i}].color'].write(light.color)
                program[f'pointLights[{i}].a'].write(light.a)
                program[f'pointLights[{i}].d'].write(light.d)
                program[f'pointLights[{i}].s'].write(light.s)

    def clear_all(self):
        self.point_lights = [] 

class Light:
    def __init__(self, ambient=0.2, diffuse=0.5, specular=1.0, color=(1.0, 1.0, 1.0)):
        self.color = glm.vec3(color)
        self.a = glm.float32(ambient)
        self.d = glm.float32(diffuse)
        self.s = glm.float32(specular)


class DirectionalLight(Light):
    def __init__(self, direction=(1.0, -1.5, -1.0), ambient=0.4, diffuse=0.6, specular=1.0, color=(1.0, 1.0, 1.0)):
        super().__init__(ambient, diffuse, specular, color)
        self.dir = glm.vec3(direction)
        self.position = glm.vec3(150, 100, -150)
        # View matrix
        self.m_view_light = self.get_view_matrix()
    
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.dir, glm.vec3(0, 1, 0) )


class PointLight(Light):
    def __init__(self, pos=(1.0, 3.0, 1.0), constant=1.0, linear=0.09, quadratic=0.032, ambient=0.0, diffuse=3.0, specular=0.5, color=(1.0, 1.0, 1.0)):
        super().__init__(ambient, diffuse, specular, color)
        self.np_pos = np.array(pos)
        self.pos = glm.vec3(pos)
        self.constant = glm.float32(constant)
        self.linear = glm.float32(linear)
        self.quadratic = glm.float32(quadratic)