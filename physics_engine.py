from physics_binary_search import *
from hitboxes import Hitbox
import numpy as np
from chunk_handler import CHUNK_SIZE
from numba import njit
from config import config
import random

#@njit
def detect_broad_collision(c1, c20, c21, c22, dim1, dim2):

    if dim1[0] == dim2[0] and dim1[1] == dim2[1] and dim1[2] == dim2[2]:
        return (c1[0] - c20)**2 + (c1[1] - c21)**2 + (c1[2] - c22)**2 <= 4*(dim1[0]**2 + dim1[1]**2 + dim1[2]**2)
    return np.linalg.norm(c1 - np.array([c20, c21, c22])) <= np.linalg.norm(dim1) + np.linalg.norm(dim2)

class PhysicsEngine():
    
    def __init__(self, gravity_strength, chunk_handler, dummy):
        
        self.gjk = GJK()
        self.gravity_strength = gravity_strength
        self.pbs = PBS(self)
        self.dummy = dummy
        self.chunk_handler = chunk_handler
        #detect_broad_collision(np.array([1, 1, 1], dtype = 'f4'), 1, 1, 1, np.array([1, 1, 1], dtype = 'f4'), np.array([1, 1, 1], dtype = 'f4'))
        
    def get_bullet_dimensions(self, pos, scale):
        
        return [pos + (x, y, z) for z in (-scale, scale) for y in (-scale, scale) for x in (-scale, scale)]
        
    def resolve_terrain_bullet_collisions(self, bullets):
        
        for bullet in bullets:
            # gets chunk and checks if position is fully filled
            chunk = self.chunk_handler.get_chunk_from_point(bullet.pos)
            if chunk is None: continue
            if chunk.field[int(bullet.pos[0]) % CHUNK_SIZE][int(bullet.pos[1]) % CHUNK_SIZE][int(bullet.pos[2]) % CHUNK_SIZE] > 0.98:
                bullet.has_collided = True
                continue
            # checks the individual triangles on the chunk cube
            for triangle in chunk.get_cube_from_point(bullet.pos):
                collided = self.gjk.get_gjk_collision(Hitbox(self.dummy, triangle, [[0, 1, 2]], (1, 1, 1), (0, 0, 0), 0, (0, 0, 0)), Hitbox(self.dummy, self.get_bullet_dimensions(bullet.pos, 0.1), [[x, y, z] for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)], [1, 1, 1]))
                if not collided: continue
                bullet.has_collided = True
    
    def resolve_object_bullet_collisions(self, objs, bullets):
    
        for obj in objs:
            obj_hitbox, obj_pos, obj_dimensions = obj.hitbox, np.array([i for i in obj.pos]), obj.hitbox.dimensions
            for bullet in bullets:
                if bullet.caster is obj: continue
                # broad collision
                if not detect_broad_collision(obj_pos, bullet.pos[0], bullet.pos[1], bullet.pos[2], obj_dimensions, np.array([1, 1, 1], dtype = 'f4')): continue
                # narrow collision
                collided = self.gjk.get_gjk_collision(obj_hitbox, Hitbox(self.dummy, [bullet.pos], [[0, 0, 0]], [1, 1, 1]))
                if not collided: continue
                bullet.has_collided = True
        
    def resolve_terrain_collisions(self, objs, delta_time):       
        player_pos = self.chunk_handler.scene.entity_handler.entities[0].obj.pos
        for obj in objs:
            # checks for simulation distance and skybox
            if not self.is_in_sim_distance(player_pos, obj.pos): continue
            for chunk in self.chunk_handler.get_close_chunks(obj):
                for cube in chunk.get_close_cubes(obj):
                    for triangle in cube:
                        
                        # regular physics calculation
                        self.dummy.set_hitbox(Hitbox(self.dummy, triangle, [[0, 1, 2]], (1, 1, 1), (0, 0, 0), 0, (0, 0, 0)))
                        
                        collided = self.gjk.get_gjk_collision(obj.hitbox, self.dummy.hitbox)
                        if not collided: continue
                        
                        obj.last_collided = 'terrain'
                        
                        self.resolve_collision(obj, self.dummy, delta_time)
        
    # object to object collisions
    def resolve_collisions(self, objs, delta_time):
        
        player_pos = self.chunk_handler.scene.entity_handler.entities[0].obj.pos
        
        for obj in objs:
            obj.last_collided = None
            
        for i, obji in enumerate(objs):
            # checks for simulation distance and skybox
            if not self.is_in_sim_distance(player_pos, obj.pos): continue
            if objs[i].obj_type == 'skybox': continue
            
            obji_immovable, obji_hitbox, obji_pos, obji_dimensions = obji.immovable, obji.hitbox, np.array([i for i in obji.pos]), obji.hitbox.dimensions
            
            for objj in objs[i+1:]:
                # checks to see if both objects cant be moved
                if obji_immovable and objj.immovable: continue
                # broad collision
                if not detect_broad_collision(obji_pos, objj.pos[0], objj.pos[1], objj.pos[2], obji_dimensions, objj.hitbox.dimensions): continue
                # narrow collision
                collided = self.gjk.get_gjk_collision(obji_hitbox, objj.hitbox)
                if not collided: continue
                # sets last collisions
                obji.last_collided, objj.last_collided = objj, obji
                # collision resolution
                self.resolve_collision(obji, objj, delta_time)
                
        return objs
    
    # determines if objects are close enough to collide
    def detect_broad_collision(self, hitbox1, hitbox2):
        
        # distance between the center of the points is less than the maximum distance of the rectangular hitbox
        return glm.length(hitbox1.get_center() - hitbox2.get_center()) <= glm.length(hitbox1.dimensions) + glm.length(hitbox2.dimensions)
    
    def resolve_collision(self, obj1, obj2, delta_time):
        
        # finds colliding polygons/edges/lines
        normal1, normal2 = self.get_collision_normal(obj1.hitbox, obj2.hitbox.get_center()), self.get_collision_normal(obj2.hitbox, obj1.hitbox.get_center())
        # moves object to position before collision
        self.pbs.uncollide_objects(obj1, obj2, normal1, normal2, delta_time)
        
        point1, point2 = self.distance_point_to_plane(obj1.hitbox, normal2, obj1.pos[1] > obj2.pos[1]), self.distance_point_to_plane(obj2.hitbox, normal1, obj1.pos[1] > obj2.pos[1])
        
        if not obj1.immovable: self.get_collision_result(obj1.hitbox, normal2, point1, 0.5, 2.5, delta_time)
        if not obj2.immovable: self.get_collision_result(obj2.hitbox, normal1, point2, 0.5, 2.5, delta_time)
        
        return obj1, obj2
    
    def get_collision_result(self, hitbox1, normal2, close_point, elasticity_factor, friction_factor, delta_time):
        
        # translational velocity
        reflected_vel = glm.reflect(hitbox1.vel, normal2)
        parallel, perpendicular = self.get_components(reflected_vel, normal2)
        
        # play sound if collision is fast
        if abs(glm.length(parallel)) > 3:
            self.chunk_handler.scene.sound_handler.play_sound(random.choice(['clonk', 'clack']))
        
        # friction and elasticity
        parallel *= elasticity_factor
        perpendicular *= (1 - friction_factor * delta_time)
        reflected_vel = parallel + perpendicular
        
        # rotational velocity
        radius = glm.normalize(hitbox1.get_center() - close_point)
        rad_par, rad_perp = self.get_components(radius, normal2)
        
        # gravitational vs lateral rotation
        if glm.length(reflected_vel) < 3 and glm.dot((0, 1, 0), normal2) > 0:
            aor = glm.cross(radius, normal2)
            
            # pretend that the objects rotation is increasing with the acceleration due to gravity if aor == hitbox1.rot_axis: vel = hitbox1.rot_vel
            #else: 
            vel = glm.dot(normal2, radius)
        else: 
            aor = glm.cross(radius, perpendicular)
            vel = glm.length(perpendicular) / (glm.length(radius) * glm.pi())
        
        # sets rotational and translational velocity variables
        hitbox1.set_vel(reflected_vel)# - rad_perp * glm.length(hitbox1.vel))
        hitbox1.set_rot_axis(aor)
        hitbox1.set_rot_vel(vel)
        
        
    def get_components(self, vec, normal):
        parallel = glm.dot(vec, normal) * normal
        perpendicular = vec - parallel
        return parallel, perpendicular
    
    def get_colliding_points(self):
    
        # creates dictionary of vertices and their closest values
        vertex_dict = {}
        vertices = []
        for vertex in self.gjk.simplex:

            minimum = glm.min(vertex[0])
            vertex_dict[minimum] = vertex[1]
            vertices.append(minimum)
            
        vertices.sort()
        
        # gets valid colliding points near minimum
        maximum = vertices[0] * 2
        colliding_points = [vertices[0]]
        for i in range(1, len(vertices)):
            
            if vertices[i] > maximum: break
            colliding_points.append(vertices[i])
            
        return [vertex_dict[i] for i in colliding_points]
            
    def get_collision_normal(self, hitbox, colliding_obj_center):
        
        normal = glm.vec3(0, 0, 0)
        
        for index in range(len(hitbox.faces)):
            test_normal = hitbox.get_face_normal(index)
            for i in range(3):
                if glm.dot(colliding_obj_center - hitbox.get_face_vertex(index, i), test_normal) <= 0: break
            
            # if successful
            else: 
                normal += test_normal
            
        if normal[0] == 0 and normal[1] == 0 and normal[2] == 0: 
            normal = colliding_obj_center - hitbox.get_center()
            if normal[0] == 0 and normal[1] == 0 and normal[2] == 0: return glm.vec3(0, 1, 0)
        
        return glm.normalize(normal)
    
    def distance_point_to_plane(self, hitbox, normal, above):
        
        vertices = hitbox.vertices
        best = ([glm.vec3(0, 0, 0)], 1e10)
        mod = 1e6
        if above: mod = -1e6
        
        for vertex in vertices:
            
            distance = abs(normal[1]*vertex[1] + normal[2]*vertex[2] + normal[0]*vertex[0] + mod) / glm.length(normal)
            distance = round(distance, 5)
            if distance < best[1]: best = ([vertex], distance)
            
        return best[0][0]
    
    def is_in_sim_distance(self, player_pos, test_pos):
        
        chunk_radius = config['simulation']['simulation_distance']
        player_pos, test_pos = [i // 10 for i in player_pos], [i // 10 for i in test_pos]
        for i in range(3):
            if not test_pos[i] - chunk_radius <= player_pos[i] <= test_pos[i] + chunk_radius: return False
        return True