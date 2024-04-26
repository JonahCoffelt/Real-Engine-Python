import math
import numpy as np

def quaternion_conjugate(quaternion):
    w, x, y, z = quaternion
    return [w, -x, -y, -z]
        
def axis_angle_to_quaternion(axis, angle):
    axis = normalize3(axis)
    rotation_quaternion = [math.cos(angle / 2)] + [a * math.sin(angle / 2) for a in axis]
    return rotation_quaternion

def euler_to_quaternion(e):
    cph, sph, cth, sth, cps, sps = math.cos(e[0]/2), math.sin(e[0]/2), math.cos(e[1]/2), math.sin(e[1]/2), math.cos(e[2]/2), math.sin(e[2]/2),
    w = cph*cth*cps + sph*sth*sps
    x = sph*cth*cps - cph*sth*sps
    y = cph*sth*cps + sph*cth*sps
    z = cph*cth*sps - sph*sth*cps
    return [w, x, y, z]

def quaternion_to_euler(q):
    w, x, y, z = q[0], q[1], q[2], q[3]
    phi = math.atan2(2 * (w * x + y * z), 1 - 2 * (x**2 + y**2))
    theta = math.pi/2 - 2 * math.atan2(math.sqrt(1 + 2 * (w * y - x * z)), math.sqrt(1 - 2 * (w * y - x * z)))
    psi = math.atan2(2 * (w * z + y * x), 1 - 2 * (y**2 + z**2))
    return phi, theta, psi

def quaternion_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2

    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

    return [w, x, y, z]

def normalize4(q):
    if (mag := np.linalg.norm(q)) != 0: return [i / mag for i in q]
    return [0, 0.57735027, 0.57735027, 0.57735027]

def normalize3(v):
    if (mag := np.linalg.norm(v)) != 0: v = [i / mag for i in v]
    return v

def get_quaternion_angle(q):
    w, x, y, z = q[0], q[1], q[2], q[3]
    if w < 0: w *= -1
    return 2 * math.acos(w)
    
def get_quaternion_axis(q, angle):
    sin = math.sin(angle/2)
    return [i/sin for i in q[1:]]

