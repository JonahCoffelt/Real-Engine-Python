from random import uniform

class BulletHandler():
    
    def __init__(self, object_handler):
        
        self.object_handler = object_handler
        self.bullets = []
        self.pe_time = 0
        self.pe_wait_time = 1/60
        
    def update(self, delta_time):
        
        # bullet movement
        for bullet in self.bullets:
            bullet.move(delta_time)
        
        # bullet collision
        self.pe_time += delta_time
        if self.pe_time > self.pe_wait_time:
            self.pe_time = 0
            self.object_handler.pe.resolve_terrain_bullet_collisions(self.bullets)
            self.object_handler.pe.resolve_object_bullet_collisions(self.object_handler.objects, self.bullets)
        
    def add_bullet(self, bullet):
        
        self.bullets.append(bullet)
        return bullet
        
class Bullet():
    
    def __init__(self, spell, bullet_handler : BulletHandler, pos, direction, launch_program, caster):
        
        # hierarchy variables
        self.caster = caster
        self.spell = spell
        self.launch_program = launch_program
        self.bullet_handler = bullet_handler
        self.life = 10
        
        # other variables
        self.direction = direction
        self.pos = pos
        self.particle_timer = 0
        self.has_collided = False
        
    def move(self, delta_time):
        
        # time decay
        self.life -= delta_time
        if self.life < 0: 
            self.remove_self()
            return
        
        # checks if bullet has collided
        if self.has_collided is True:
            self.execute()
            return
        
        # visuals
        if self.particle_timer > 0.05:
            self.spawn_particle()
            self.particle_timer = 0
        self.particle_timer += delta_time
        
        # movement
        self.pos, self.direction = self.launch_program(self.pos, self.direction, delta_time)
        
    def spawn_particle(self):
        color_min, color_max = self.spell.color
        r = uniform(color_min[0], color_max[0])
        g = uniform(color_min[1], color_max[1])
        b = uniform(color_min[2], color_max[2])

        self.bullet_handler.object_handler.scene.particle_handler.add_particles(clr = (r, g, b), pos = self.pos, vel = (0, 0, 0), accel = (0, 0, 0), type = 2, scale = 0.25)
        
    def execute(self):
        
        # bullet aftermath
        self.bullet_handler.object_handler.scene.chunk_handler.modify_terrain(-self.spell.terrain_radius, self.pos, self.spell.element.terrain_material, width = int(abs(self.spell.terrain_radius)) + 1)
        self.bullet_handler.object_handler.scene.particle_handler.add_explosion(pos = self.pos, radius = self.spell.radius, clr = self.spell.color)
        
        # applies effects to nearby entities
        entities = self.bullet_handler.object_handler.scene.entity_handler.get_entities_in_radius(self.pos, self.spell.radius)
        for entity, direction in entities.items():
            entity.take_hit(self.spell, self.pos)
        
        # removes bullet from game
        self.remove_self()
        
    def remove_self(self):
        
        # removes from handler lists
        self.bullet_handler.bullets.remove(self)
        
        # delete self from system
        del self