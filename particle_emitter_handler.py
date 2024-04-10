from random import uniform as rand


class ParticleEmitterHandler:
    def __init__(self, particle_handler):
        self.particle_handler = particle_handler
        self.emitters = []

        self.templates = {
            'fire' : [
                [10.0, 15, 1, 3, 0.35, 1.8, 0.1, (.9, .35, .15), .1, (0.0, 0.0, 0.0), (0.5, 0.5, 0.5), (0.0, 3.0, 0.0), (1.0, 1.5, 1.0), (0.0, 2.0, 0.0), (1.0, 0.3, 1.0)],
                [10.0, 15, 1, 3, 0.5, 1.0, 0.1, (.9, .7, .15), .1, (0.0, 1.0, 0.0), (0.2, 0.2, 0.2), (0.0, 4.0, 0.0), (0.5, 2.0, 0.5), (0.0, 2.0, 0.0), (1.0, 0.3, 1.0)],
                [10.0, 15, 1, 3, 0.5, 0.6, 0.1, (.7, .7, .7), .2, (0.0, 1.3, 0.0), (0.3, 0.3, 0.3), (0.0, 4.0, 0.0), (1.0, 3.0, 1.0), (0.0, 2.0, 0.0), (2.0, 1.0, 2.0)]
                ]
        }
    
    def update(self, dt):
        for emitter in self.emitters:
            emitter.update(dt)

    def add_emitter(self, template=False, pos=(0.0, 0.0, 0.0), particle_attribs=[[10.0, 5, 1, 3, 1.0, 1.0, 0.1, (.9, .9, .9), .1, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 7.0, 0.0), (1.0, 1.0, 1.0), (0.0, -10.0, 0.0), (0.0, 0.0, 0.0)]]):
        """
        Attributes:
            particle_attribs: list - Contains all attribs of all particles for the emitter
                [0]    emitter_life: float - Total time the emitter exists for
                [1]    n: int - The number of particle groups spawned per frame (Will not spawn more than 1 group per frame, so FPS is a hard max)
                [2]    group_size: int - Number of particles spawned per group
                [3]    type: int - The type of the particle (2 = 2D, 3 = 3D)
                [4]    life: float - Time the particle exists
                [5]    scale: float - The max size of the particle
                [6]    scale_variance: float - Range of scale in either direction
                [7]    color: tuple - Average spawning color of a particle
                [8]    color_variance: float - Range in either direction of RGB values uniformly ditributed from the mean
                [9]    position: tuple - Average spawn location of a particle
                [10]   position_variance: tuple - The furthest point a particle can spawn from the origin in each axis. Uniformly distributed
                [11]   velocity: tuple - Average spawning velocity of a particle
                [12]   velocity_variance: tuple - Range of velocities (See position_variance)
                [13]   acceleration: tuple - Average spawning acceleration of a particle
                [14]   acceleration_variance: tuple - Range of accelerations (See position_variance)
        """
        if template: particle_attribs = self.templates[template]
        self.emitters.append(Emitter(self.particle_handler, pos, particle_attribs))


class Emitter:
    def __init__(self, particle_handler, pos, particle_attribs):
        self.particle_handler = particle_handler
        self.particles = particle_attribs
        self.global_pos = pos
        self.timers = [0 for i in range(len(particle_attribs))]
    
    def update(self, dt):
        for i, particle in enumerate(self.particles):
            self.timers[i] += dt
            if self.timers[i] <= 1/particle[1]: continue
            self.timers[i] = 0

            for n in range(particle[2]):
                scale = particle[5] + rand(-particle[6], particle[6])

                color = particle[7]
                var = rand(-particle[8], particle[8])
                color = (color[0] + var, color[1] + var, color[2] + var)

                pos = particle[9]
                var = particle[10]
                pos = (pos[0] + self.global_pos[0] + rand(-var[0], var[0]), pos[1] + self.global_pos[1] + rand(-var[1], var[1]), pos[2] + self.global_pos[2] + rand(-var[2], var[2]))

                vel = particle[11]
                var = particle[12]
                vel = (vel[0] + rand(-var[0], var[0]), vel[1] + rand(-var[1], var[1]), vel[2] + rand(-var[2], var[2]))

                accel = particle[13]
                var = particle[14]
                accel = (accel[0] + rand(-var[0], var[0]), accel[1] + rand(-var[1], var[1]), accel[2] + rand(-var[2], var[2]))

                self.particle_handler.add_particles(type=particle[3], life=particle[4], pos=pos, clr=color, scale=scale, vel=vel, accel=accel)