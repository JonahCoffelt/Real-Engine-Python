import numpy as np
from random import randint

# rooms are 10 by 10

def generate_rooms(field : np.array, max_room_count, min_size = (2, 1, 2), max_size = (3, 2, 3), room_tries = 5):
    
    field_shape = field.shape
    
    for i in range(max_room_count):
        
        # generates room size
        room_size = [randint(min_size[i], max_size[i]) for i in range(3)]
        for j in room_tries:
            room_location = [randint(0, field_shape[i] - room_size[i]) for i in range(3)]
            for x in range(room_location, room_location - room_size):
                ...
    
# delaunay tetralation
def generate_paths():
    ...
    
def generate_field(x, y, z):
    return np.zeros((x, y, z), dtype = 'B')

dungeon = generate_field(12, 3, 12)
