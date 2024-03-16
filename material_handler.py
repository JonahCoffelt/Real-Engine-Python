import glm


class MaterialHandler:
    def __init__(self, textures):
        self.textures = textures
        
        self.materials = {}

        self.materials['container'] = BaseMaterial('container', 'container_specular', 64.0, self.textures)
        self.materials['metal_box'] = BaseMaterial('metal_box', 'metal_box', 64.0, self.textures)
        self.materials['wooden_box'] = BaseMaterial('wooden_box', 'wooden_box', 16.0, self.textures)
        self.materials['meshes'] = BaseMaterial('metal_box', 'metal_box', 64.0, self.textures)
        self.materials['cat'] = BaseMaterial('cat', 'cat', 64.0, self.textures)


class BaseMaterial:
    def __init__(self, diffuse: str, specular: str, specular_constant: str, textures):
        self.d = textures[diffuse]
        self.s = textures[specular]

        self.spec_const = glm.float32(specular_constant)

    def write(self, program):
        program['material.d'] = 1
        self.d.use(location=1)
        program['material.s'] = 2
        self.s.use(location=2)

        program['material.spec_const'].write(self.spec_const)
