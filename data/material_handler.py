import glm
import cudart


class MaterialHandler:
    def __init__(self, textures):
        self.textures = textures
        
        self.materials = {}

        self.materials['container'] = BaseMaterial('container', 'container_specular', 64.0, self.textures)
        self.materials['metal_box'] = BaseMaterial('metal_box', 'metal_box', 64.0, self.textures)
        self.materials['wooden_box'] = BaseMaterial('wooden_box', 'wooden_box', 16.0, self.textures)
        self.materials['meshes'] = BaseMaterial('metal_box', 'metal_box', 64.0, self.textures)
        self.materials['cat'] = BaseMaterial('cat', 'cat', 64.0, self.textures)
        self.materials['diceguy'] = BaseMaterial('diceguy', 'diceguy', 64.0, self.textures)
        self.materials['d4'] = BaseMaterial('d4', 'd4', 64.0, self.textures)
        self.materials['d6'] = BaseMaterial('d6', 'd6', 64.0, self.textures)
        self.materials['d20'] = BaseMaterial('d20', 'd20', 64.0, self.textures)

class BaseMaterial:
    def __init__(self, diffuse: str, specular: str, specular_constant: str, textures):
        self.d = textures[diffuse]
        self.s = textures[specular]

        self.spec_const = glm.float32(specular_constant)

    def write(self, program, multiplier=(1.0, 1.0, 0.5)):
        offset = glm.vec3(multiplier)
        program['material.offset'].write(offset)
        program['material.d'] = 1
        self.d.use(location=1)
        program['material.s'] = 2
        self.s.use(location=2)

        program['material.spec_const'].write(self.spec_const)
