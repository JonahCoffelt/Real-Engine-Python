import numpy as np
import glm

class ParticleHandler:
    def __init__(self, ctx, programs, cam) -> None:
        self.programs = programs
        self.ctx = ctx
        self.cam = cam
        self.particle_vbo = ParticleVBO(ctx)
        self.particles = [Particle(self.ctx, self.cam, self.programs['particle'], self.particle_vbo)]

    def render(self):
        self.programs['particle']['m_view'].write(self.cam.m_view)
        self.programs['particle']['m_proj'].write(self.cam.m_proj)
        for particle in self.particles:
            particle.render()


class Particle:
    def __init__(self, ctx, cam, program, vbo):
        self.ctx = ctx
        self.cam = cam
        self.program = program
        self.vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        
        self.pos = glm.vec3(0.0, 0.0, 0.0)

    def get_model_matrix(self):
        m_model = glm.mat4()
        # Translate
        m_model = glm.translate(m_model, self.pos)
        # Rotate
        #cam_dir = glm.vec3(np.cos(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch)), np.sin(np.deg2rad(self.cam.pitch)), np.sin(np.deg2rad(self.cam.yaw)) * np.cos(np.deg2rad(self.cam.pitch)))
        #print(cam_dir)
        yaw = np.arctan2(self.pos.x - self.cam.position.x, self.pos.z - self.cam.position.z)
        pitch = np.arctan2(np.sqrt(np.power(self.pos.x - self.cam.position.x, 2) + np.power(self.pos.z - self.cam.position.z, 2)), self.pos.y - self.cam.position.y)
        m_model = glm.rotate(m_model, pitch, glm.vec3(1, 0, 0))
        #m_model = glm.rotate(m_model, yaw, glm.vec3(0, 1, 0))

        return m_model

    def render(self):
        self.program['m_model'].write(self.get_model_matrix())
        self.vao.render()


class ParticleVBO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format = '3f 3f'
        self.attribs = ['in_position', 'in_color']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],  # Bottom Left
                     [ 1, -1, 0],  # Bottom Right
                     [ 1,  1, 0],   # Top Right
                     [-1,  1, 0],  # Top Left
                     ])
        
        indicies = [(1, 0, 3),
                    (1, 3, 2),]
        
        #verticies = np.array([
        #            [-1, -1, -1],  # Bottom Left Back 0
        #            [ 1, -1, -1],  # Bottom Right Back 1
        #            [ 1,  1, -1],  # Top Right Back 2
        #            [-1,  1, -1],  # Top Left Back 3
        #            [-1, -1, 1 ],  # Bottom Left Front 4
        #            [ 1, -1, 1 ],  # Bottom Right Front 5
        #            [ 1,  1, 1 ],  # Top Right Front 6
        #            [-1,  1, 1 ],  # Top Left Front 7
        #            ])

        #indicies = [(1, 0, 3),
        #            (1, 3, 2),
        #            (7, 4, 5),
        #            (6, 7, 5),
        #            (7, 6, 3),
        #            (3, 6, 2),
        #            (1, 5, 0),
        #            (0, 5, 4),
        #            (4, 7, 0),
        #            (0, 7, 3),
        #            (1, 6, 5),
        #            (2, 6, 1)
        #            ]

        vertex_data = self.get_data(verticies, indicies)

        color_data = np.array([[1.0, 0.0, 1.0] for i in range(len(indicies) * 3)], dtype='f4')

        vertex_data = np.hstack([vertex_data, color_data])
        return vertex_data
        color = (1.0, 1.0, 0.0)
        return np.array([[[0, 1, 0, *color], [-1, -1, 0, *color], [1, -1, 0, *color]]], dtype='f4')
    
    @staticmethod
    def get_data(verticies, indicies):
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
