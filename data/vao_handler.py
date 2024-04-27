from data.vbo_handler import VBOHandler
from data.shader_program_handler import ProgramHandler
#import cudart


class VAOHandler:
    def __init__(self, ctx, scene):
        self.ctx = ctx

        scene.tick()
        self.vbo_handler = VBOHandler(self.ctx)
        scene.tick()
        self.program_handler = ProgramHandler(self.ctx)

        self.vaos = {}


    def set_up(self):
        self.add_vao('cube', 'default')
        self.add_vao('quad', 'mesh')
        self.add_vao('cat', 'default')
        self.add_vao('diceguy', 'default')
        self.add_vao('d4', 'default')
        self.add_vao('d6', 'default')
        self.add_vao('d20', 'default')
        self.vaos['skybox'] = self.get_vao(program=self.program_handler.programs['skybox'], 
                                         vbo=self.vbo_handler.vbos['skybox'])

    def add_vao(self, vbo, prog):
        self.vaos[vbo] = self.get_vao(program=self.program_handler.programs[prog], 
                                         vbo=self.vbo_handler.vbos[vbo])
        self.vaos[f'shadow_{vbo}'] = self.get_vao(program=self.program_handler.programs['shadow_map'], 
                                         vbo=self.vbo_handler.vbos[vbo])
        self.vaos[f'normal_{vbo}'] = self.get_vao(program=self.program_handler.programs['buffer_normal'], 
                                         vbo=self.vbo_handler.vbos[vbo])
        self.vaos[f'depth_{vbo}'] = self.get_vao(program=self.program_handler.programs['buffer_depth'], 
                                         vbo=self.vbo_handler.vbos[vbo])

    def get_vao(self, program, vbo):
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        return vao
    
    def destroy(self):
        self.vbo_handler.destroy()
        self.program_handler.destroy()