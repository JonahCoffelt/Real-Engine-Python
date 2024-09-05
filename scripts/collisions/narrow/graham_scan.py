import glm
from math import atan2

from scripts.generic.math_functions import is_ccw_turn

def graham_scan(points:list[glm.vec2]) -> None:
    """converts list of arbitrary points into polygon sorted ccw"""
    # get pivot point
    pivot = min(points, key=lambda p: (p.y, p.x))
    points.remove(pivot)
    
    # sort points by polar angle and start hull
    points = sorted(points, key=lambda p: (get_polar_angle(pivot, p), glm.length(pivot - p)))
    hull = [pivot, points.pop(0)]
    
    for point in points:
        while len(hull) > 1 and not is_ccw_turn(hull[-2], hull[-1], point):
            hull.pop()
        hull.append(point)
    
    return hull
    
def get_polar_angle(pivot:glm.vec2, point:glm.vec2) -> float:
    """gets the polar angle between two points from the horizontal"""
    vector = point - pivot
    return atan2(vector.y, vector.x)