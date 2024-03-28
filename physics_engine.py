from physics_binary_search import *
from spatial_partitioning import SpationalPartitionHandler
from hitboxes import Hitbox
import numpy as np

class PhysicsEngine():
    
    def __init__(self, gravity_strength, dummy, chunk_handler, object_handler):
        
        self.gravity_strength = gravity_strength
        self.gjk = GJK()
        self.pbs = PBS(self)
        self.dummy = dummy
        self.chunk_handler = chunk_handler
        self.spatial_partition_handler = SpationalPartitionHandler(object_handler)
        
    def resolve_terrain_collisions(self, objs, delta_time):
        
        for obj in objs:
            for chunk in self.chunk_handler.get_close_chunks(obj):
                for cube in chunk.get_close_cubes(obj):
                    for triangle in cube:
                        
                        # terrain value testing
                        """for vertex in obj.hitbox.vertices:
                            if """
                        
                        # regular physics calculation
                        self.dummy.set_hitbox(Hitbox(self.dummy, triangle, [[0, 1, 2]], (1, 1, 1), (0, 0, 0), 0, (0, 0, 0)))
                        
                        collided = self.gjk.get_gjk_collision(obj.hitbox, self.dummy.hitbox)
                        if not collided: continue
                        
                        obj.last_collided = 'terrain'
                        
                        self.resolve_collision(obj, self.dummy, delta_time)
        
    # object to object collisions
    def resolve_collisions(self, objs, delta_time):
    
        for i in range(len(objs)):
            if objs[i].obj_type == 'skybox': continue
            for j in range(i + 1, len(objs)):
                # checks to see if both objects cant be moved
                if objs[i].immovable and objs[j].immovable: continue
                # broad collision
                if not self.detect_broad_collision(objs[i].hitbox, objs[j].hitbox): continue
                # bullet to bullet collision
                if objs[i].obj_type == 'wooden_box' == objs[j].obj_type: continue
                    #if self.chunk_handler.scene.entity_handler.spell_handler.bullet_handler.is_same_spell(objs[i], objs[j]): continue
                # narrow collision
                collided = self.gjk.get_gjk_collision(objs[i].hitbox, objs[j].hitbox)
                if not collided: continue
                # sets last collisions
                objs[i].last_collided, objs[j].last_collided = objs[j], objs[i]
                # collision resolution
                self.resolve_collision(objs[i], objs[j], delta_time)
                
        return objs
        
        for obj in objs:
            if obj.obj_type == 'skybox': continue
            # gets nearby objects
            nearby = self.spatial_partition_handler.get_close_objects(obj)
            for near in nearby:
                # if both objects cant be moved
                if obj.immovable and near.immovable: continue
                # broad collision
                #if not self.detect_broad_collision(obj.hitbox, near.hitbox): continue
                # bullet to bullet collision
                if obj.obj_type == 'wooden_box' == near.obj_type: continue
                    #if self.chunk_handler.scene.entity_handler.spell_handler.bullet_handler.is_same_spell(obj, near): continue
                # narrow collision
                collided = self.gjk.get_gjk_collision(obj.hitbox, near.hitbox)
                if not collided: continue
                # sets last collisions
                obj.last_collided, near.last_collided = near, obj
                # collision resolution
                self.resolve_collision(obj, near, delta_time)
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
        
        point1, point2 = self.distance_point_to_plane(obj1.hitbox, normal2), self.distance_point_to_plane(obj2.hitbox, normal1)
        
        if not obj1.immovable: self.get_collision_result(obj1.hitbox, normal2, point1, 0.5, 10, delta_time)
        if not obj2.immovable: self.get_collision_result(obj2.hitbox, normal1, point2, 0.5, 10, delta_time)
        
        return obj1, obj2
    
    def get_collision_result(self, hitbox1, normal2, close_point, elasticity_factor, friction_factor, delta_time):
        
        # translational velocity
        reflected_vel = glm.reflect(hitbox1.vel, normal2)
        parallel, perpendicular = self.get_components(reflected_vel, normal2)
        
        # friction and elasticity
        parallel *= elasticity_factor
        perpendicular *= (1 - friction_factor * delta_time)
        reflected_vel = parallel + perpendicular
        
        # rotational velocity
        radius = glm.normalize(hitbox1.get_center() - close_point)
        rad_par, rad_perp = self.get_components(radius, normal2)
        
        # gravitational vs lateral rotation
        if glm.length(reflected_vel) < 1 and glm.dot((0, 1, 0), normal2) > 0:
            aor = glm.cross(radius, normal2)
            
            # pretend that the objects rotation is increasing with the acceleration due to gravity
            if aor == hitbox1.rot_axis: vel = hitbox1.rot_vel
            else: vel = glm.dot(normal2, radius) * 0.1
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
    
    def get_colliding_points(self, simplex):
    
        # creates dictionary of vertices and their closest values
        vertex_dict = {}
        vertices = []
        for vertex in simplex:

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
    
    def distance_point_to_plane(self, hitbox, normal):
        
        vertices = hitbox.vertices
        best = ([glm.vec3(0, 0, 0)], 1e10)
        
        for vertex in vertices:
            
            distance = abs(normal[1]*vertex[1] + normal[2]*vertex[2] + normal[0]*vertex[0] - 1e6) / glm.length(normal)
            distance = round(distance, 5)
            if distance < best[1]: best = ([vertex], distance)
            
        return best[0][0]