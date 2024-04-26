import random

class LoadZoneHandler():
    
    def __init__(self, scene):
        
        self.scene = scene
        # name : zone
        self.active = {}
        self.inactive = {
            'hub' : LoadZone(self, (20, 5, 20), (4, 4, 4), 'hub', (0, 1, 1))
        }
        
        # timing
        self.max_time = 1/5
        self.time = self.max_time
        
    def update(self, delta_time):
        
        # timing
        self.time -= delta_time
        if self.time > 0: return
        self.time = self.max_time
        
        zones_to_remove = []
        # updates all objects
        for name, zone in self.active.items():
            zone.update()
            if zone.player_is_in(): 
                match zone.function:
                    case 'dungeon':
                        # move to next dungeon
                        self.scene.power += 10
                        self.scene.enter_dungeon(self.scene.power)
                        zones_to_remove.append(zone)
                    case 'hub':
                        # move to next dungeon can only be one warp in hub
                        self.scene.enter_dungeon(self.scene.power)
                        self.move_to_inactive(name)
                        break
                        
        for zone in zones_to_remove:
            self.delete_from_active(zone)
            
    def move_to_active(self, name):
        self.active[name] = self.inactive.pop(name)
    def move_to_inactive(self, name):
        self.inactive[name] = self.active.pop(name)
    def delete_from_active(self, zone):
        for key, value in self.active.items():
            if value is zone: 
                del self.active[key]
                break
    
    # adding load zones to handler
    def add_inactive(self, name, pos, dim, function, color = (1, 1, 1), particle_density = 2):
        self.inactive[name] = LoadZone(self, pos, dim, function, color, particle_density)
    def add_active(self, name, pos, dim, function, color = (1, 1, 1), particle_density = 2):
        self.active[name] = LoadZone(self, pos, dim, function, color, particle_density)
        
class LoadZone():
    
    # pos -, -, -
    def __init__(self, load_zone_handler : LoadZoneHandler, pos, dim, function, color = (1, 1, 1), particle_density = 2):
        
        self.load_zone_handler = load_zone_handler
        self.pos = pos
        self.dim = dim
        self.color = color
        self.particle_density = particle_density
        self.function = function
        
    def update(self):

        # handles particles
        locations = [[self.pos[i] + random.uniform(0, self.dim[i]) * [1, 0, 1][i] for i in range(3)] for i in range(self.particle_density)]
        for location in locations:
            self.load_zone_handler.scene.particle_handler.add_particles(pos = location, clr = self.color, vel = (0, 0, 0), accel = (0, 3, 0))
            
    def player_is_in(self):
        
        # determines if player is in loadzone
        for i in range(3):
            if not self.pos[i] <= self.load_zone_handler.scene.entity_handler.entities[0].obj.pos[i] <= self.pos[i] + self.dim[i]: return False
        # determined that player is in loadzone
        return True
