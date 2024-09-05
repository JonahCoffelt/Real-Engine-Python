import glm
from scripts.generic.math_functions import get_support_point, triple_product

# main gjk handler
def get_gjk_collision(points1:list, points2:list, position1:glm.vec3, position2:glm.vec3, iterations:int = 50) -> tuple:
    """gets boolean and simplex from gjk"""
    # gets starting values
    direction_vector = position1 - position2
    simplex          = [get_support_point(points1, points2, direction_vector)]
    
    # points direction vector to the origin
    direction_vector = -simplex[0][0]
    
    # main gjk loop
    for _ in range(iterations):
        # gets support point and checks if its across the origin
        test_point = get_support_point(points1, points2, direction_vector)
        if glm.dot(test_point[0], direction_vector) < 0: return False, simplex
        
        # if successful add point and handle simplex
        simplex.append(test_point)
        check, direction_vector, simplex = handle_simplex(simplex)
        
        if check: return True, simplex
    return False, simplex

# simplex handling
def handle_simplex(simplex:list) -> tuple:
    """calls proper functions for gjk simplex based on size"""
    match len(simplex):
        case 2: return handle_simplex_line(simplex)
        case 3: return handle_simplex_triangle(simplex)
        case 4: return handle_simplex_tetra(simplex)
        case _: assert False, 'simplex has unsupported size :('
        
def handle_simplex_line(simplex:list) -> tuple:
    """returns perpendicular vector to simplex line"""
    vector_ab = simplex[1][0] - simplex[0][0]
    return False, triple_product(vector_ab, -simplex[0][0], vector_ab), simplex

def handle_simplex_triangle(simplex:list) -> tuple:
    """returns triangle normal vector pointed towards the origin"""
    directional_vector = glm.cross(simplex[1][0] - simplex[0][0], simplex[2][0] - simplex[0][0])
    return False, -directional_vector if glm.dot(directional_vector, -simplex[0][0]) < 0 else directional_vector, simplex

def handle_simplex_tetra(simplex:list) -> tuple:
    """runs collision test and removes point if false"""
    vec_da = simplex[3][0] - simplex[0][0]
    vec_db = simplex[3][0] - simplex[1][0]
    vec_dc = simplex[3][0] - simplex[2][0]
    vec_do = -simplex[3][0]
    
    epsilon = -1e-4
    
    # Randomize the order of checking the vectors
    vectors = [(glm.cross(vec_da, vec_db), 2), (glm.cross(vec_dc, vec_da), 1), (glm.cross(vec_db, vec_dc), 0)]
    
    for normal_vec, index in vectors:
        dot_product = glm.dot(normal_vec, vec_do)
        if dot_product > epsilon:
            simplex.pop(index)
            return False, normal_vec, simplex
    return True, None, simplex