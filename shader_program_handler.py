

class ProgramHandler:
    def __init__(self, app):
        self.ctx = app.ctx
        self.programs = {}

        self.programs['default'] = self.get_program('default')

    def get_program(self, name):
        with open(f'shaders/{name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def destroy(self):
        [program.release() for program in self.programs]