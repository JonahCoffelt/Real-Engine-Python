import glm
from scripts.collisions.narrow.gjk import get_support_point
from scripts.generic.math_functions import get_average_point

# main epa handler
def get_epa_from_gjk(points1:list, points2:list, polytope:list) -> tuple:
    """gets normal and distance from expanding polytope expansion"""
    # each list indexes the points of a face, always the same for converted simplexes
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    # calculate face normals
    avg_pt = get_average_point(polytope)
    normals = [calculate_polytope_normal(face, polytope, avg_pt) for face in faces]
    # minimum collision response variables
    while True: 
        nearest_normal, nearest_distance, nearest_face = get_nearest(polytope, faces, normals)
        new_point = get_support_point(points1, points2, nearest_normal)
        # tests new point distance
        if glm.length(new_point[0]) - nearest_distance < 0 or new_point in polytope:
            # find contact points
            return nearest_normal, nearest_distance, polytope, nearest_face
        polytope.append(new_point) # add support point to polytope
        faces, normals = get_new_faces_and_normals(faces, normals, polytope) # find new faces on polytope
        
# polytope handling
def get_nearest(polytope:list, faces:list, normals:list) -> int:
    """returns the normal and distance of nearest face"""
    nearest, nearest_distance, nearest_face = None, 1e10, None
    for i, face in enumerate(faces):
        if (distance := abs(glm.dot(polytope[face[0]][0], normals[i]))) < nearest_distance: nearest, nearest_distance, nearest_face = normals[i], distance, face
    return nearest, nearest_distance, nearest_face

def get_new_faces_and_normals(faces:list, normals:list, polytope:list) -> tuple:
    """
    returns new faces and normals of polytope with added point
    polytope must contain recent support point as last index
    """
    sp_index, visible_indexes = len(polytope) - 1, []
    for i, normal in enumerate(normals):
        avg_point = (polytope[faces[i][0]][0] + polytope[faces[i][1]][0] + polytope[faces[i][2]][0]) / 3
        if glm.dot(normal, polytope[sp_index][0]) < 1e-5 or glm.dot(polytope[sp_index][0] - avg_point, normal) < 1e-5: continue
        visible_indexes.append(i)
    visible_indexes.sort() # sort for removing
    # finds new edges
    edges = []
    for i in visible_indexes:
        for edge in get_face_edges(faces[i]):
            if edge in edges: edges.remove(edge)
            else: edges.append(edge)
    # remove visible faces
    while len(visible_indexes) > 0:
        faces.pop(visible_indexes[-1])
        normals.pop(visible_indexes[-1])
        visible_indexes.pop()
    # adds new faces
    for edge in edges: faces.append((edge[0], edge[1], sp_index))
    # calculate new normals
    avg_pt = get_average_point(polytope)
    for face in faces[len(normals):]: normals.append(calculate_polytope_normal(face, polytope, avg_pt))
    return faces, normals

def get_face_edges(face:list) -> list:
    """returns the edge indexes to the polytope points"""
    return [(one, two) if (one := face[i - 1]) < (two := face[i]) else (two, one) for i in range(3)]

def calculate_polytope_normal(face:list, polytope:list, reference_center:glm.vec3) -> glm.vec3:
    """calculates the given normal from 3 points on the polytope"""
    one, two, three = polytope[face[0]][0], polytope[face[1]][0], polytope[face[2]][0]
    normal = glm.cross(one-two, one-three)
    # calculate average point
    if glm.dot((one + two + three)/3 - reference_center, normal) < 0: normal *= -1
    return glm.normalize(normal)