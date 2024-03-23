import numpy as np
import glm
import random

class ParticleHandler:
    def __init__(self, ctx, programs, cam) -> None:
        self.programs = programs
        self.ctx = ctx
        self.cam = cam
        self.particle_vbo = ParticleVBO(ctx)
        self.particles = [Particle(self.ctx, self.programs['particle'], self.particle_vbo, pos=(random.randrange(-10, 10) for i in range(3))) for particle in range(50)]

    def render(self):
        self.programs['particle']['m_view'].write(self.cam.m_view)
        self.programs['particle']['m_proj'].write(self.cam.m_proj)

        cam_pos = self.cam.position
        particle_dict = {i : glm.length(particle.pos - cam_pos) for i, particle in enumerate(self.particles)}
        particle_dict = sorted(particle_dict.items(), key=lambda x:x[1])
        order = [particle[0] for particle in particle_dict]

        for particle_index in list(reversed(order)):
            self.particles[particle_index].render(self.cam)

    def add_particles(self, clr=(1.0, 1.0, 1.0), pos=(0, 0, 0), vel=(0, 3, 0), accel=(0, -10, 0)):
            self.particles.append(Particle(self.ctx, self.programs['particle'], self.particle_vbo, clr=clr, pos=pos, vel=vel, accel=accel))

    def update(self, dt):
        removes = []
        if dt < .5:
            for particle in self.particles:
                particle.update(dt)
                if particle.life < 0:
                    removes.append(particle)
        for particle in removes:
            self.particles.remove(particle)


class Particle:
    def __init__(self, ctx, program, vbo, clr=(1.0, 1.0, 1.0), pos=(0, 0, 0), vel=(0, 4, 0), accel=(0, -1, 0)):
        self.ctx = ctx
        self.program = program
        self.pos = glm.vec3(*pos)
        self.color = glm.vec3(*clr)
        #self.color = glm.vec3(*[random.uniform(0, 1) for i in range(3)])
        self.vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)

        self.life = 2
        self.position = np.array([self.pos.x, self.pos.y, self.pos.z], dtype='f4')
        self.velocity = np.array([*vel], dtype='f4')
        self.acceleration = np.array([*accel], dtype='f4')

    
    def update(self, dt):
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

        self.pos = glm.vec3(self.position)

        self.life -= dt

    def get_model_matrix(self, cam):
        m_model = glm.mat4()
        # Translate
        m_model = glm.translate(m_model, self.pos)
        # Rotate
        yaw = np.arctan2(self.pos.x - cam.position.x, self.pos.z - cam.position.z)
        pitch = -np.arctan2(self.pos.y - cam.position.y, np.sqrt(np.power(self.pos.x - cam.position.x, 2) + np.power(self.pos.z - cam.position.z, 2)))
        m_model = glm.rotate(m_model, yaw, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, pitch, glm.vec3(1, 0, 0))

        return m_model

    def render(self, cam):
        self.program['m_model'].write(self.get_model_matrix(cam))
        self.program['u_Color'].write(self.color)
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

        vertex_data = self.get_data(verticies, indicies)

        color_data = np.array([[1.0, 1.0, 1.0] for i in range(len(indicies) * 3)], dtype='f4')

        vertex_data = np.hstack([vertex_data, color_data])
        return vertex_data
    
    @staticmethod
    def get_data(verticies, indicies):
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
