import math
import numpy as np

def quaternion_conjugate(quaternion):
    w, x, y, z = quaternion
    return [w, -x, -y, -z]
        
def axis_angle_to_quaternion(axis, angle):
    axis = np.array(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    rotation_quaternion = np.array([math.cos(angle / 2)] + list(math.sin(angle / 2) * axis))
    return rotation_quaternion
        
def rotate_quaternion_by_another(q, rotation):
    # Ensure the input quaternions are numpy arrays
    q = np.array(q)
    rotation = np.array(rotation)

    # Normalize the rotation quaternion
    rotation /= np.linalg.norm(rotation)

    # Multiply the quaternions to perform rotation
    rotated_q = quaternion_multiply(rotation, q)
    return rotated_q

def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

    return [w, x, y, z]