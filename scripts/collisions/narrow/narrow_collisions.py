import glm
from scripts.collisions.narrow.epa import get_epa_from_gjk
from scripts.collisions.narrow.gjk import get_gjk_collision
from scripts.collisions.narrow.contact_manifold import get_contact_manifold

# main collision function
def get_narrow_collision(points1:list, points2:list, position1:glm.vec3, position2:glm.vec3) -> tuple:
    """returns the normalized normal vector of the collision and the distance"""
    # determine if narrow collision has occured
    have_collided, simplex = get_gjk_collision(points1, points2, position1, position2)
    if not have_collided: return glm.vec3(0, 0, 0), 0, glm.vec3(0, 0, 0)
    # get polytope from narrow collision
    normal, distance, polytope, face = get_epa_from_gjk(points1, points2, simplex)
    # get manifold from collision
    contact_plane_point = get_contact_plane_point(polytope, face)
    manifold = get_contact_manifold(contact_plane_point, normal, points1, points2, polytope, face)
    # fallback if manifold fails to generate
    if len(manifold) == 0: return glm.normalize(normal), distance, [calculate_contact_point(points1, points2, polytope, face, normal)] # get_contact_plane_point(polytope, face)
    return glm.normalize(normal), distance, manifold # change phsyics handler to accept multiple collision points

def get_contact_plane_point(polytope, face) -> glm.vec3:
    """gets the most likely point for the contact plane"""
    n1, n2 = glm.cross(polytope[face[2]][2] - polytope[face[1]][2], polytope[face[2]][2] - polytope[face[0]][2]), glm.cross(polytope[face[2]][1] - polytope[face[1]][1], polytope[face[2]][1] - polytope[face[0]][1])
    d = glm.cross(n1, n2)
    if (deno := glm.dot(n1, d)) == 0: return estimate_contact_plane_point(polytope, face) # fall back if planes dont intersect
    r0 = polytope[face[2]][2]
    t = -glm.dot(n1, r0 - polytope[face[2]][1]) / deno
    return r0 + t * d
    
def estimate_contact_plane_point(polytope, face) -> glm.vec3:
    point2 = (polytope[face[0]][2] + polytope[face[1]][2] + polytope[face[2]][2]) / 3
    point1 = (polytope[face[0]][1] + polytope[face[1]][1] + polytope[face[2]][1]) / 3
    return (point1 + point2) / 2

def calculate_contact_point(points1, points2, polytope, face, normal):
    """Calculates the contact points on the original objects."""
    # Get the vertices of the nearest face
    a, b, c = polytope[face[0]][0], polytope[face[1]][0], polytope[face[2]][0]

    # Calculate the barycentric coordinates with respect to the origin
    def signed_volume(p1, p2, p3):
        return glm.dot(glm.cross(p1 - p3, p2 - p3), normal) / 6.0

    total_volume = signed_volume(a, b, c)
    if total_volume == 0:
        return glm.vec3(0, 0, 0)

    volume_pbc = signed_volume(glm.vec3(0), b, c)
    volume_pca = signed_volume(glm.vec3(0), c, a)
    volume_pab = signed_volume(glm.vec3(0), a, b)

    u = volume_pbc / total_volume
    v = volume_pca / total_volume
    w = volume_pab / total_volume

    # Normalize the barycentric coordinates if necessary
    sum_barycentric = u + v + w
    if sum_barycentric != 0:
        u /= sum_barycentric
        v /= sum_barycentric
        w /= sum_barycentric

    # Retrieve original support points from Minkowski difference
    def get_support_points_from_minkowski(points1, points2, minkowski_point):
        direction = minkowski_point
        support1 = get_furthest_point(points1, direction)
        support2 = get_furthest_point(points2, -direction)
        return support1, support2

    support1_a, support2_a = get_support_points_from_minkowski(points1, points2, a)
    support1_b, support2_b = get_support_points_from_minkowski(points1, points2, b)
    support1_c, support2_c = get_support_points_from_minkowski(points1, points2, c)

    # Interpolate the contact points on the original shapes
    contact_point1 = u * support1_a + v * support1_b + w * support1_c
    contact_point2 = u * support2_a + v * support2_b + w * support2_c

    return contact_point1 # Optionally, you can return contact_point2 as well

def get_furthest_point(points:list, direction_vector:glm.vec3) -> glm.vec3: # may need to be normalized
    """finds furthest point in given direction"""
    best_point, best_dot = glm.vec3(0, 0, 0), -1e6
    for point in points: 
        if (dot := glm.dot(point, direction_vector)) > best_dot: best_point, best_dot = point, dot
    return best_point
