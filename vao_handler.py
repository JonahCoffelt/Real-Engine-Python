from vbo_handler import VBOHandler
from shader_program_handler import ProgramHandler


class VAOHandler:
    def __init__(self, app):
        self.app = app

        self.vbo_handler = VBOHandler(self.app.ctx)
        self.program_handler = ProgramHandler(self.app)

        self.vaos = {}
        self.vaos['cube'] = self.get_vao(program=self.program_handler.programs['default'], 
                                         vbo=self.vbo_handler.vbos['cube'])

    def get_vao(self, program, vbo):
        print(vbo.format, *vbo.attribs)
        vao = self.app.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)])
        return vao
    
    def desstroy(self):
        self.vbo_handler.destroy()
        self.program_handler.destroy()