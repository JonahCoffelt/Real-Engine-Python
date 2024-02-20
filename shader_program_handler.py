

class ProgramHandler:
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = {}

        self.programs['default'] = self.get_program('default')
        self.programs['skybox'] = self.get_program('skybox')
        self.programs['shadow_map'] = self.get_program('shadow_map')

    def get_program(self, name):
        with open(f'shaders/{name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def destroy(self):
        [program.release() for program in self.programs]