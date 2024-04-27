import numpy as np
from numba import njit
import random
import moderngl as mgl
from data.particle_emitter_handler import ParticleEmitterHandler
#import cudart


#  Particle Format
#  x, y, z, r, g, b, scale, life ...
#  vx, vy, vz, ax, ay, az


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
    particle_instances[:,8:11] += particle_instances[:,11:14] * dt
    particle_instances[:,:3] += particle_instances[:,8:11] * dt
    particle_instances[:,7] -= dt/3
    return particle_instances

@njit
def get_alive(particles):
    return particles[particles[:, 7] >= 0]

class ParticleHandler:
    def __init__(self, ctx, programs, ico_vbo, cam) -> None:
        self.programs = programs
        self.ctx = ctx
        self.cam = cam
        self.emitter_handler = ParticleEmitterHandler(self, cam)

        self.vbo_2d = ParticleVBO(ctx)
        self.ico_vbo = ico_vbo
        self.empty_particle = np.array([0.0 for i in range(14)])

        self.particle_cube_size = 18
        self.order_update_timer = 0

        self.particle_instances_2d = np.zeros(shape=(1,14), dtype='f4')                   
        self.particle_instances_3d = np.zeros(shape=(1,14), dtype='f4')

        self.instance_buffer_2d = ctx.buffer(reserve=(14 * 3) * (self.particle_cube_size ** 3))
        self.instance_buffer_3d = ctx.buffer(reserve=(14 * 3) * (self.particle_cube_size ** 3))

        cam_pos = self.cam.position
        self.particle_instances_2d = np.array(sort_particles(self.particle_instances_2d, np.array([cam_pos.x, cam_pos.y, cam_pos.z])), dtype='f4', order='C')
        
        self.vbo_2d = self.vbo_2d
        self.vao_2d = self.ctx.vertex_array(self.programs['particle'], [(self.vbo_2d.vbo, self.vbo_2d.format, *self.vbo_2d.attribs), 
                                                                     (self.instance_buffer_2d, '3f 3f 1f 1f /i', 'in_instance_pos', 'in_instance_color', 'scale', 'life')
                                                                     ], 
                                                                     skip_errors=True)
        self.vbo_3d = self.ico_vbo
        self.vao_3d = self.ctx.vertex_array(self.programs['particle3d'], [(self.ico_vbo.vbo, self.ico_vbo.format, *self.ico_vbo.attribs), 
                                                                     (self.instance_buffer_3d, '3f 3f 1f 1f /i', 'in_instance_pos', 'in_instance_color', 'scale', 'life')
                                                                     ], 
                                                                     skip_errors=True)

    def render(self):
        cam_pos = self.cam.position
        self.programs['particle']['m_view'].write(self.cam.m_view)
        self.programs['particle']['m_proj'].write(self.cam.m_proj)
        self.programs['particle']['cam'].write(cam_pos)
        self.programs['particle3d']['m_view'].write(self.cam.m_view)
        self.programs['particle3d']['m_proj'].write(self.cam.m_proj)

        alive_particles = get_alive(self.particle_instances_3d)
        self.instance_buffer_3d.write(np.array(alive_particles[:,:8], order='C'))
        self.vao_3d.render(instances=(len(alive_particles)))

        self.ctx.enable(flags=mgl.BLEND)
        alive_particles = get_alive(self.particle_instances_2d)
        self.instance_buffer_2d.write(np.array(alive_particles[:,:8], order='C'))
        self.vao_2d.render(instances=(len(alive_particles)))
        self.ctx.disable(flags=mgl.BLEND)

    def add_particles(self, type=2, life=1.0, pos=(0, 0, 0), clr=(1.0, 1.0, 1.0), scale=1.0, vel=(0, 3, 0), accel=(0, -10, 0)):
        if type == 2 and len(self.particle_instances_2d) < (self.particle_cube_size ** 3): self.particle_instances_2d = np.vstack((np.array([*pos, *clr, scale, life, *vel, *accel]), self.particle_instances_2d), dtype='f4')
        elif len(self.particle_instances_3d) < (self.particle_cube_size ** 3): self.particle_instances_3d = np.vstack((np.array([*pos, *clr, scale, life, *vel, *accel]), self.particle_instances_3d), dtype='f4')

    def update(self, dt):
        cam_pos = self.cam.position
        self.emitter_handler.update(dt, cam_pos)
        # Update 2D Particle Matrix & Sort by distance from camera
        self.particle_instances_2d = get_alive(self.particle_instances_2d)
        self.particle_instances_2d = update_particle_matrix(self.particle_instances_2d, dt)
        self.particle_instances_2d = np.array(sort_particles(self.particle_instances_2d, np.array([cam_pos.x, cam_pos.y, cam_pos.z])), dtype='f4')
        # Update 3D Particle Matrix
        self.particle_instances_3d = get_alive(self.particle_instances_3d)
        self.particle_instances_3d = update_particle_matrix(self.particle_instances_3d, dt)
        
    # particle effects
    def add_fire(self, pos):
        self.add_particles(type=3, life=.5, scale=2, pos=pos, clr=(random.uniform(.75, 1), random.uniform(.25, .5),.25), vel=(random.uniform(-2, 2) + pos[0], random.uniform(3, 5), random.uniform(-2, 2) + pos[2]), accel=(random.uniform(-1, 1) - pos[0] * 3, 2, random.uniform(-1, 1) - pos[2] * 3))
        self.add_particles(type=3, life=.5, scale=2, pos=(pos[0]/2, pos[1] + 1, pos[2]/2), clr=(random.uniform(.75, 1), random.uniform(.4, .9),.25), vel=(random.uniform(-1, 1) + pos[0], random.uniform(4, 6), random.uniform(-1, 1) + pos[2]), accel=(random.uniform(-1, 1) - pos[0] * 3, 2, random.uniform(-1, 1) - pos[2] * 3))
        smoke_color = random.uniform(.5, .9)
        self.add_particles(type=3, pos=(0, 3, 0), clr=(smoke_color, smoke_color, smoke_color), scale=.5, vel=(random.uniform(-1, 1), random.uniform(1, 6), random.uniform(-1, 1)), accel=(random.uniform(-1, 1), random.uniform(-1, 3), random.uniform(-1, 1)))
        
    def add_explosion(self, pos, radius, clr, count = 15):
        # explosion particle effect will extend slightly beyond radius
        for _ in range(count):
            color_min, color_max = clr
            r = random.uniform(color_min[0], color_max[0])
            g = random.uniform(color_min[1], color_max[1])
            b = random.uniform(color_min[2], color_max[2])
            p = np.array([i + random.uniform(-1.0, 1.0) * radius for i in pos])
            direction = p - pos
            scale = radius*2 - np.linalg.norm(direction) + 0.5
            self.add_particles(pos = p, type = 3, life = 0.25, scale = scale, clr = (r, g, b), vel = direction, accel = [random.uniform(-1, 1) for _ in range(3)])

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