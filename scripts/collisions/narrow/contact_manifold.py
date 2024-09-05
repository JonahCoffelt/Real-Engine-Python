import glm
from random import randint

from scripts.collisions.narrow.line_intersections import line_line_intersect, line_poly_intersect
from scripts.collisions.narrow.graham_scan import graham_scan
from scripts.collisions.narrow.sutherland_hodgman import sutherland_hodgman

# sutherland hodgman clipping algorithm
def get_contact_manifold(contact_plane_point:glm.vec3, contact_plane_normal:glm.vec3, points1:list[glm.vec3], points2:list[glm.vec3], polytope, face) -> list[glm.vec3]:
    """computes the contact manifold for a collision between two nearby polyhedra"""
    # gets near points to be considered for clipping
    points1 = get_past_points(contact_plane_point, contact_plane_normal, points1)
    points2 = get_past_points(contact_plane_point, -contact_plane_normal, points2)
    
    if len(points1) == 0 or len(points2) == 0: return []
    
    # project vertices onto the 2d plane
    points1 = project_points(contact_plane_point, contact_plane_normal, points1)
    points2 = project_points(contact_plane_point, contact_plane_normal, points2)
    
    # check if collsion was on a vertex
    if len(points1) == 1: return points1
    if len(points2) == 1: return points2
    
    # convert points to 2d for intersection algorithms
    points1, u1, v1 = points_to_2d(contact_plane_point, contact_plane_normal, points1)
    points2, u2, v2 = points_to_2d(contact_plane_point, contact_plane_normal, points2) #TODO precalc orthogonal basis for 2d conversion
    
    # convert arbitrary points to polygon
    if len(points1) > 2: points1 = graham_scan(points1)
    if len(points2) > 2: points2 = graham_scan(points2)
    
    # run clipping algorithms
    manifold = []
    is_line1, is_line2 = len(points1) == 2, len(points2) == 2
    if is_line1 and is_line2: manifold = line_line_intersect(points1, points2)
    else: 
        if is_line1: manifold = line_poly_intersect(points1, points2)
        elif is_line2: manifold = line_poly_intersect(points2, points1)
        else: manifold = sutherland_hodgman(points1, points2)
        
    # fall back if manifold fails to develope
    if len(manifold) == 0: return []
    # convert inertsection algorithm output to 3d
    return points_to_3d(u1, v1, contact_plane_point, manifold)

# plane functions
def get_past_points(contact_plane_point:glm.vec3, contact_plane_normal:glm.vec3, points:list[glm.vec3], epsilon:float = 1e-3) -> list[glm.vec3]:
    """returns the points on the wrong side of the contact plane"""
    return list(filter(lambda point: glm.dot(contact_plane_normal, point - contact_plane_point) > -epsilon, points))
    
# def get_near_points(contact_plane_point:glm.vec3, contact_plane_normal:glm.vec3, points:list[glm.vec3], epsilon:float = 1e-3) -> list[glm.vec3]:
#     """get the points closest to the contact plane"""
#     distances = {}
#     closest_distance = 1e10
#     for point in points: 
#         distance = distance_to_plane(contact_plane_point, contact_plane_normal, point)
#         # determine if points need to be considered for closest points
#         if distance < closest_distance + epsilon: 
#             if distance not in distances: distances[distance] = []
#             distances[distance].append(point)
#             if distance < closest_distance: closest_distance = distance
#     # adds points to closest point array of they are within error
#     near_points = []
#     for distance, possible_points in distances.items():
#         if distance <= closest_distance + epsilon: near_points += possible_points
#     return near_points
    
def distance_to_plane(contact_plane_point:glm.vec3, contact_plane_normal:glm.vec3, point:glm.vec3) -> float:
    """gets the smallest distance a point is from a plane"""
    return glm.dot(point - contact_plane_point, contact_plane_normal) #TODO check this formula

def project_points(contact_plane_point:glm.vec3, contact_plane_normal:glm.vec3, points:list[glm.vec3]) -> list[glm.vec3]:
    """gets the projected positions of the given points onto the given plane"""
    return [point - glm.dot(point - contact_plane_point, contact_plane_normal) * contact_plane_normal for point in points]

def points_to_2d(contact_plane_point:glm.vec3, contact_plane_normal:glm.vec3, points:list[glm.vec3]) -> tuple[list[glm.vec2], glm.vec3, glm.vec3]:
    """converts a list of points on a plane to their 2d representation"""
    # generate a new basis
    k = get_noncolinear_vector(contact_plane_normal)
    u = glm.normalize(glm.cross(contact_plane_normal, k))
    v = glm.cross(contact_plane_normal, u)
    
    # convert points to new basis
    return [glm.vec2(glm.dot(vec := point - contact_plane_point, u), glm.dot(vec, v)) for point in points], u, v
    
def points_to_3d(u:glm.vec3, v:glm.vec3, contact_plane_point:glm.vec3, points:list[glm.vec2]) -> list[glm.vec3]:
    """converts a list of points on a plane to their 3d representation"""
    for i, point in enumerate(points):
        points[i] = contact_plane_point + point.x * u + point.y * v
    return points
    
# vector math
def get_noncolinear_vector(vector:glm.vec3) -> glm.vec3:
    """generates a non colinear vector based on the given vector"""
    test_vector = (1, 1, 1)
    while glm.cross(test_vector, vector) == (0, 0, 0):
        val = randint(0, 7) # 000 to 111
        test_vector = (val & 1, val & 2, val & 4) # one random for three digits
    return test_vector