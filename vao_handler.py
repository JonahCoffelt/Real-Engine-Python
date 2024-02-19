from vbo_handler import VBOHandler
from shader_program_handler import ProgramHandler


class VAOHandler:
    def __init__(self, ctx):
        self.ctx = ctx

        self.vbo_handler = VBOHandler(self.ctx)
        self.program_handler = ProgramHandler(self.ctx)

        self.vaos = {}

        self.add_vao('cube', 'default')
        self.add_vao('cat', 'default')
        
        self.vaos['skybox'] = self.get_vao(program=self.program_handler.programs['skybox'], 
                                         vbo=self.vbo_handler.vbos['skybox'])

    def add_vao(self, vbo, prog):
        self.vaos[vbo] = self.get_vao(program=self.program_handler.programs[prog], 
                                         vbo=self.vbo_handler.vbos[vbo])
        self.vaos[f'shadow_{vbo}'] = self.get_vao(program=self.program_handler.programs['shadow_map'], 
                                         vbo=self.vbo_handler.vbos[vbo])

    def get_vao(self, program, vbo):
        print(vbo.format, *vbo.attribs)
        vao =  self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        return vao
    
    def desstroy(self):
        self.vbo_handler.destroy()
        self.program_handler.destroy()