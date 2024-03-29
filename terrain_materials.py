import numpy as np

material_IDs = {
    0 : np.array([0.2, 0.3, 0.9], dtype='f4'),  # Water
    1 : np.array([0.1, 0.9, 0.2], dtype='f4'),  # Grass
    2 : np.array([0.5, 0.3, 0.2], dtype='f4'),  # Dirt
    3 : np.array([0.5, 0.5, 0.5], dtype='f4'),  # Stone
    4 : np.array([0.9, 0.9, 0.9], dtype='f4'),  # Snow
}

color_to_ID = {}