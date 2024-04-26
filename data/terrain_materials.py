import numpy as np
from data.element_handler import ElementHandler

material_IDs = {
    0 : np.array([0.2, 0.3, 0.9], dtype='f4'),  # Water
    1 : np.array([0.1, 0.9, 0.2], dtype='f4'),  # Grass
    2 : np.array([0.5, 0.3, 0.2], dtype='f4'),  # Dirt
    3 : np.array([0.5, 0.5, 0.5], dtype='f4'),  # Stone
    4 : np.array([0.9, 0.9, 0.9], dtype='f4'),  # Snow
    5 : np.array([0.5, 0.4, 0.2], dtype='f4'),  # Wood
}

# adds elements to materials list
element_handler, index = ElementHandler(), len(material_IDs)
for element in element_handler.elements.values():
    material_IDs[index] = np.array(element.color, dtype = 'f4')
    index += 1

color_to_ID = {}