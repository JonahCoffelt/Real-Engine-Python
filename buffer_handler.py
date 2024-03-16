BUFFERS = {
    # Name : Prorgam
    'frame' : 'buffer_frame',
    'normal' : 'buffer_normal',
    'depth' : 'buffer_depth',
    'edge_detect' : 'edge_detect'
}


class BufferHandler:
    def __init__(self, scene):
        self.scene = scene
        self.ctx = scene.ctx
        # Dictionary containing all buffers (not including ctx.screen)
        self.buffers = {}
        # Depth buffer used for all other buffers
        self.depth_renderbuffer = self.ctx.depth_renderbuffer(self.scene.graphics_engine.app.win_size)
        # Create standard buffers
        for buffer in BUFFERS: self.buffers[buffer] = self.get_buffer(buffer, BUFFERS[buffer])


    
    def get_buffer(self, name, program):
        texture_handler = self.scene.texture_handler
        vao_handler = self.scene.vao_handler
        program_hanler = vao_handler.program_handler

        # Make the texture, shader program and VAO
        texture_handler.textures[f'buffer_{name}'] = texture_handler.get_empty_texture()
        program_hanler.programs[program] = program_hanler.get_program(program)
        vao_handler.vaos[f'buffer_{name}'] = vao_handler.get_vao(program = program_hanler.programs[program], 
                                                               vbo = vao_handler.vbo_handler.vbos['frame'])
        
        # Create the buffer
        buffer = Buffer(self.ctx, texture_handler.textures[f'buffer_{name}'], 
                        vao_handler.vaos[f'buffer_{name}'], self.depth_renderbuffer)
        
        return buffer

class Buffer:
    def __init__(self, ctx, texture, vao, depth_buffer):
        self.texture = texture
        self.fbo = ctx.framebuffer(color_attachments=[self.texture], depth_attachment=depth_buffer)
        self.vao = vao

    def use(self):
        self.fbo.clear()
        self.fbo.use()