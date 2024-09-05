import glm

from scripts.generic.math_functions import is_ccw_turn
from scripts.collisions.narrow.line_intersections import line_line_intersect

def sutherland_hodgman(subject:list[glm.vec2], clip:list[glm.vec2]) -> list[glm.vec2]:
    """determines the clipped polygon vertices from ccw oriented polygons"""
    output_poly = subject
    
    for i in range(len(clip)):
        input_poly = output_poly
        output_poly = []
        
        edge_start, edge_end = clip[i], clip[(i + 1) % len(clip)]
        for j in range(len(input_poly)):
            prev_point, curr_point = input_poly[j - 1], input_poly[j]

            if is_ccw_turn(curr_point, edge_start, edge_end):
                if not is_ccw_turn(prev_point, edge_start, edge_end):
                    output_poly += line_line_intersect([edge_end, edge_start], [prev_point, curr_point])
                output_poly.append(curr_point)
            elif is_ccw_turn(prev_point, edge_start, edge_end):
                output_poly += line_line_intersect([edge_end, edge_start], [prev_point, curr_point])
                
    return output_poly
