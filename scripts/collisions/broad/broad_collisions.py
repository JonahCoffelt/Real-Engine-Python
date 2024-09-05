import glm

def get_broad_collision(collider1, collider2):
    return glm.length(collider1.geometric_center - collider2.geometric_center) < glm.length(collider1.dimensions) + glm.length(collider2.dimensions)