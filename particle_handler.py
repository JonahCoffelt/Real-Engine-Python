import numpy as np
import glm
from numba import njit
import random
import moderngl as mgl


@njit
def distance(a, b):
    return np.sum((a - b) **2, axis=1)

@njit
def sort_particles(particles_instances, cam_position):
    particles = distance(particles_instances[:,:3], cam_position).reshape(particles_instances.shape[0], 1)
    particles_with_distances = np.hstack((particles, particles_instances))
    particles_with_distances = particles_with_distances[particles_with_distances[:, 0].argsort()]
    return particles_with_distances[:,1:][::-1]

@njit
def update_particle_matrix(particle_instances, dt):
    particle_instances[:,6:9] += particle_instances[:,9:12] * dt
    particle_instances[:,:3] += particle_instances[:,6:9] * dt
    particle_instances[:,12] -= dt/3
    return particle_instances

class ParticleHandler:
    def __init__(self, ctx, programs, ico_vbo, cam) -> None:
        self.programs = programs
        self.ctx = ctx
        self.cam = cam
        self.vbo_2d = ParticleVBO(ctx)
        self.ico_vbo = ico_vbo

        self.particle_cube_size = 10

        self.order_update_timer = 0

        self.particle_instances_2d = np.array([[x * 3, y * 3, z * 3, .3, (y % 10) / 20, (z % 10) / 20 + .5, 
                                             random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)] for x in range(self.particle_cube_size) for y in range(self.particle_cube_size) for z in range(self.particle_cube_size)], dtype='f4')
        self.particle_instances_3d = np.array([[x * 3, y * 3, z * 3, .3, (y % 10) / 20, (z % 10) / 20 + .5, 
                                        random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)] for x in range(self.particle_cube_size) for y in range(self.particle_cube_size) for z in range(self.particle_cube_size)], dtype='f4')

        self.instance_buffer_2d = ctx.buffer(reserve=24 * (self.particle_cube_size ** 3))
        self.instance_buffer_3d = ctx.buffer(reserve=24 * (self.particle_cube_size ** 3))

        cam_pos = self.cam.position
        self.particle_instances_2d = np.array(sort_particles(self.particle_instances_2d, np.array([cam_pos.x, cam_pos.y, cam_pos.z])), dtype='f4')
        
        self.vbo_2d = self.vbo_2d
        self.vao_2d = self.ctx.vertex_array(self.programs['particle'], [(self.vbo_2d.vbo, self.vbo_2d.format, *self.vbo_2d.attribs), 
                                                                     (self.instance_buffer_2d, '3f 3f /i', 'in_instance_pos', 'in_instance_color')
                                                                     ], 
                                                                     skip_errors=True)
        self.vbo_3d = self.ico_vbo
        self.vao_3d = self.ctx.vertex_array(self.programs['particle3d'], [(self.ico_vbo.vbo, self.ico_vbo.format, *self.ico_vbo.attribs), 
                                                                     (self.instance_buffer_3d, '3f 3f /i', 'in_instance_pos', 'in_instance_color')
                                                                     ], 
                                                                     skip_errors=True)

    def render(self):
        cam_pos = self.cam.position
        self.programs['particle']['m_view'].write(self.cam.m_view)
        self.programs['particle']['m_proj'].write(self.cam.m_proj)
        self.programs['particle']['cam'].write(cam_pos)
        self.programs['particle3d']['m_view'].write(self.cam.m_view)
        self.programs['particle3d']['m_proj'].write(self.cam.m_proj)
        self.programs['particle3d']['cam'].write(cam_pos)

        #self.ctx.enable(flags=mgl.BLEND)
        #alive_particles = self.particle_instances_2d[self.particle_instances_2d[:, -1] >= 0]
        #self.instance_buffer_2d.write(np.array(alive_particles[:,:6], order='C'))
        #self.vao_2d.render(instances=(len(alive_particles)))
        #self.ctx.disable(flags=mgl.BLEND)

        alive_particles = self.particle_instances_3d[self.particle_instances_3d[:, -1] >= 0]
        self.instance_buffer_3d.write(np.array(alive_particles[:,:6], order='C'))
        self.vao_3d.render(instances=(len(alive_particles)))

    def add_particles(self, clr=(1.0, 1.0, 1.0), pos=(0, 0, 0), vel=(0, 3, 0), accel=(0, -10, 0)):
        self.particles.append(Particle(self.ctx, self.programs['particle'], self.particle_vbo, clr=clr, pos=pos, vel=vel, accel=accel))

    def update(self, dt):
        if dt > .5: return
        self.order_update_timer += dt
        self.particle_instances_2d = update_particle_matrix(self.particle_instances_2d, dt)
        self.particle_instances_3d = update_particle_matrix(self.particle_instances_3d, dt)
        if self.order_update_timer > .1:
            self.order_update_timer = 0
            cam_pos = self.cam.position
            self.particle_instances_2d = np.array(sort_particles(self.particle_instances_2d, np.array([cam_pos.x, cam_pos.y, cam_pos.z])), dtype='f4')


class Particle:
    def __init__(self, ctx, program, vbo, pos=(0, 0, 0), vel=(0, 4, 0), accel=(0, -1, 0)):
        self.ctx = ctx
        self.program = program
        self.pos = glm.vec3(*pos)
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


class ParticleVBO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.format = '3f'
        self.attribs = ['in_position']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],  # Bottom Left
                     [ 1, -1, 0],  # Bottom Right
                     [ 1,  1, 0],   # Top Right
                     [-1,  1, 0],  # Top Left
                     ])
        
        indicies = [(1, 0, 3),
                    (1, 3, 2),]

        vertex_data = self.get_data(verticies, indicies)

        return vertex_data
    
    @staticmethod
    def get_data(verticies, indicies):
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        return vbo
    
