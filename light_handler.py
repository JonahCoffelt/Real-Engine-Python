import glm


class LightHandler:
    def __init__(self):
        self.dir_light = DirectionalLight(color=(1.0, 1.0, 1.0))
        self.point_lights = [PointLight(pos=(1, 1, 1), color=(3.0, 0.0, 0.0), diffuse=3), PointLight(pos=(-10, 1, 1), color=(0.0, 3.0, 0.0)), PointLight(pos=(10, 1, 15), color=(0.0, 0.0, 3.0))]

    def write(self, program, dir=True, point=True):
        if dir:
            program['dir_light.direction'].write(self.dir_light.dir)
            program['dir_light.color'].write(self.dir_light.color)
            program['dir_light.a'].write(self.dir_light.a)
            program['dir_light.d'].write(self.dir_light.d)
            program['dir_light.s'].write(self.dir_light.s)
        if point:
            for i, light in enumerate(self.point_lights):
                program[f'pointLights[{i}].pos'].write(light.pos)
                program[f'pointLights[{i}].constant'].write(light.constant)
                program[f'pointLights[{i}].linear'].write(light.linear)
                program[f'pointLights[{i}].quadratic'].write(light.quadratic)
                program[f'pointLights[{i}].color'].write(light.color)
                program[f'pointLights[{i}].a'].write(light.a)
                program[f'pointLights[{i}].d'].write(light.d)
                program[f'pointLights[{i}].s'].write(light.s)



class Light:
    def __init__(self, ambient=0.2, diffuse=0.5, specular=1.0, color=(1.0, 1.0, 1.0)):
        self.color = glm.vec3(color)
        self.a = glm.float32(ambient)
        self.d = glm.float32(diffuse)
        self.s = glm.float32(specular)


class DirectionalLight(Light):
    def __init__(self, direction=(1.0, -1.0, 1.0), ambient=0.2, diffuse=0.8, specular=1.0, color=(1.0, 1.0, 1.0)):
        super().__init__(ambient, diffuse, specular, color)
        self.dir = glm.vec3(direction)
        self.position = glm.vec3(50, 50, -10)
        # View matrix
        self.m_view_light = self.get_view_matrix()
    
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.dir, glm.vec3(0, 1, 0) )


class PointLight(Light):
    def __init__(self, pos=(1.0, 3.0, 1.0), constant=1.0, linear=0.09, quadratic=0.032, ambient=1.0, diffuse=1.0, specular=1.0, color=(1.0, 1.0, 1.0)):
        super().__init__(ambient, diffuse, specular, color)
        self.pos = glm.vec3(pos)
        self.constant = glm.float32(constant)
        self.linear = glm.float32(linear)
        self.quadratic = glm.float32(quadratic)