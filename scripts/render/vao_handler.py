from scripts.render.vbo_handler import VBOHandler
from scripts.render.shader_handler import ShaderHandler


class VAOHandler:
    """
    Stores VBO and shader handlers. Creates VAOs
    """
    def __init__(self, project):
        self.project = project
        self.ctx = self.project.ctx
    
        self.shader_handler = ShaderHandler(self.project)
        self.vbo_handler = VBOHandler(self.ctx)

        self.vaos = {}
        self.add_vao()
        self.add_vao('cow', 'default', 'cow')
        self.add_vao('bunny', 'default', 'bunny')
        self.add_vao('lucy', 'default', 'lucy')

    def add_vao(self, name: str='cube', program_key: str='default', vbo_key: str='cube'):
        """
        Adds a new VAO with a program and VBO. Creates an empty instance buffer
        """
        # Get program an vbo
        program = self.shader_handler.programs[program_key]
        vbo = self.vbo_handler.vbos[vbo_key]

        # Make the VAO
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)

        # Save th VAO
        self.vaos[name] = vao
    
    def release(self):
        """
        Releases all VAOs and shader programs in handler
        """
        
        for vao in self.vaos.values():
            vao.release()

        self.vbo_handler.release()
        self.shader_handler.release()