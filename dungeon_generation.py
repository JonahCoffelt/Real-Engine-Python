import numpy as np
import random
from copy import deepcopy

class DungeonHandler():
    
    # layout: x and y dimensions of dungeon
    def __init__(self, layout = (20, 3, 20)):
        
        # room name : room object
        self.rooms = {
            'spawn' : Room('room-northdead', [1, 1, 1], [[[0, 0, 0], 0]]),
            'north dead' : Room('room-northdead', [1, 1, 1], [[[0, 0, 0], 0]]),
            'east dead' : Room('room-eastdead', [1, 1, 1], [[[0, 0, 0], 1]]),
            'south dead' : Room('room-southdead', [1, 1, 1], [[[0, 0, 0], 2]]),
            'west dead' : Room('room-westdead', [1, 1, 1], [[[0, 0, 0], 3]]),
            '1 north hall' : Room('room-nshall', [1, 1, 1], [[[0, 0, 0], 0], [[0, 0, 0], 2]]),
            'omni hall' : Room('room-omnihall', [1, 1, 1], [[[0, 0, 0], 0], [[0, 0, 0], 1], [[0, 0, 0], 2], [[0, 0, 0], 3]]),
            'diner' : Room('room-diner', [2, 1, 2], [[[0, 0, 0], 3], [[0, 0, 0], 2], [[1, 0, 1], 0], [[1, 0, 1], 1]]),
            'north stair' : Room('room-northstair', [2, 2, 1], [[[1, 1, 0], 0], [[0, 0, 0], 2]]),
            'big library' : Room('room-biglibrary', [3, 2, 3], [[[1, 0, 0], 3], [[0, 0, 1], 2], [[2, 0, 1], 0], [[1, 0, 2], 1], [[1, 1, 0], 3], [[0, 1, 1], 2], [[2, 1, 1], 0], [[1, 1, 2], 1]]),
        }
        # 0 = empty, 1 = used
        self.gen_layout = np.zeros(layout, dtype='f4') 
        self.invalid_random_room_ids = [
            'spawn',
            'boss'
        ]
        # chunk : Room object
        self.room_spawns = {}
        self.layout_dim = layout
        
    def reset(self, layout = None):
        
        if layout is None:
            layout = self.layout_dim
        self.gen_layout = np.zeros(layout, dtype='f4') 
        self.layout_dim = layout
        self.room_spawns = {}
        
    def save_room(self, room, pos : tuple):
        
        self.room_spawns[tuple(pos)] = room
        
        # overrides empty spaces in gen_layout
        self.gen_layout[pos[0]:pos[0]+room.dim[0], pos[1]:pos[1]+room.dim[1], pos[2]:pos[2]+room.dim[2]] += np.ones(room.dim, dtype = 'f4')
        
    def reserve_spot(self, pos):
        
        self.gen_layout[pos[0]:pos[0]+1, pos[1]:pos[1]+1, pos[2]:pos[2]+1] += np.ones((1, 1, 1), dtype = 'f4')
        
    def generate_dungeon(self):
        
        # create spawn room in middle back
        spawn_pos = (0, 0, self.gen_layout.shape[0]//2)
        spawn_room = self.rooms['spawn']
        self.save_room(spawn_room, spawn_pos)
        self.generate_branch((1, 0, self.gen_layout.shape[0]//2), 0)
        if np.sum(self.gen_layout) < self.get_layout_volume() // 3:
            self.reset()
            self.generate_dungeon()
        
    def get_layout_volume(self):
        
        shape = self.gen_layout.shape
        return shape[0] * shape[1] * shape[2]
            
    def generate_branch(self, door_pos, door_dir, reserved_spots = []):
        # generates a room with the given parameters
        required_door_dir = (door_dir + 2) % 4
        room_generated = False
        while not room_generated:
            # gets random room with door oriented the correct way
            room = self.get_room_with_door(required_door_dir)
            # gets doors facing the correct direction
            doors = room.door_data[:]
            valid_doors = []
            for door in doors:
                if door[1] is not required_door_dir: continue
                valid_doors.append(door)
            # tests doors to get valid room spawn 
            random.shuffle(valid_doors)
            for door in valid_doors:
                # gets room alignment with given door and checks if valid placement
                pos = [door_pos[i] - door[0][i] for i in range(3)]
                safe_door_pos = self.get_door_exit_pos(door, pos)
                if not self.room_can_be_placed(room, pos, safe_door_pos, reserved_spots): continue
                # adds room to position
                self.save_room(room, pos)
                doors.remove(door)
                room_generated = True
                break
            
        reserved_spots = []
        for door in doors:
            exit_pos = self.get_door_exit_pos(door, pos)
            #print([pos[i] + door[0][i] for i in range(3)], door_pos)
            self.reserve_spot(exit_pos)
            reserved_spots.append(exit_pos)
        #print(reserved_spots)
            
        # generate branch from open doors
        for door in doors:
            self.generate_branch(self.get_door_exit_pos(door, pos), door[1], reserved_spots)
                
    def room_can_be_placed(self, room, pos, safe_door_pos, reserved_spots):
        
        # removes reserved spots from generation layout
        temp_layout = deepcopy(self.gen_layout)
        for spot in reserved_spots:
            self.gen_layout[spot[0]][spot[1]][spot[2]] = 0

        check = self.room_in_bounds(room.dim, pos) and self.room_is_free(room.dim, pos) and self.doors_in_bounds(room, pos) and self.doors_are_free(room, pos, safe_door_pos)
        
        # restores gen layout
        self.gen_layout = deepcopy(temp_layout)
        
        return check
    
    def doors_are_free(self, room, pos, safe_door_pos):
        for door in room.door_data:
            new_pos = self.get_door_exit_pos(door, pos)
            if sum([safe_door_pos[i] is not new_pos[i] for i in range(3)]) == 0: continue
            if not self.point_is_free(new_pos): return False
        return True

    def doors_in_bounds(self, room, pos):
        for door in room.door_data:
            new_pos = self.get_door_exit_pos(door, pos)
            # checks the new position of the door
            if not self.point_is_in_bounds(new_pos): return False
        return True
    
    def get_door_exit_pos(self, door, pos):
        
        # gets the new position of the door
        new_pos = [pos[i] + door[0][i] for i in range(3)]
        match door[1]:
            case 0: new_pos[0] += 1
            case 1: new_pos[2] += 1
            case 2: new_pos[0] -= 1
            case 3: new_pos[2] -= 1
            case _: False, 'Door orientation does not exist'
        return new_pos
    
    def room_in_bounds(self, dim, pos):
        #print(dim, pos)
        for i in range(3):
            if pos[i] + dim[i] - 1 >= self.gen_layout.shape[i]: return False
            if pos[i] < 0: return False
        return True
    
    def room_is_free(self, dim, pos):
        
        return np.sum(self.gen_layout[pos[0]:pos[0]+dim[0], pos[1]:pos[1]+dim[1], pos[2]:pos[2]+dim[2]]) == 0
                
    def point_is_in_bounds(self, pos):
        
        for i in range(3):
            if pos[i] >= self.gen_layout.shape[i] or pos[i] < 0: return False
        return True
    
    # returns if a room space in the generation layout is being used or not
    def point_is_free(self, pos):
        
        return self.gen_layout[pos[0]][pos[1]][pos[2]] == 0
        
    def get_room_with_door(self, door_dir):

        while True:
            room = self.get_random_room()
            for door in room.door_data:
                if door[1] == door_dir: return room
            
    def get_random_room(self):

        room_id = 'spawn'
        while room_id in self.invalid_random_room_ids:
            room_id = random.choice(list(self.rooms.keys()))
        return self.rooms[room_id]

class Room():
    
    # door data stored as 
    # [(x, y, z),  pos x = 1, pos z = 2, neg x = 3, neg z = 4]
    def __init__(self, file_name, dim, door_data : list):
        
        self.file_name = file_name
        self.door_data = door_data
        self.dim = dim