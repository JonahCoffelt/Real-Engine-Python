import numpy as np
from data.terrain_materials import color_to_ID, material_IDs
from data.marching_cubes_chunk import CHUNK_SIZE

def get_field_from_voxels(path, dim):
    field = np.zeros(shape=(dim[0], dim[1], dim[2])) - 1
    materials = np.zeros(shape=(dim[0] + 2, dim[1] + 2, dim[2] + 2)) + 5
    with open(f'voxelModels/{path}.ply', 'r') as file:
        while file.readline() != 'end_header\n':...
        line = file.readline()
        while line != '':
            line_data = list(map(int, line.split(' ')))
            x, z, y = line_data[0] + dim[0]//2, line_data[1] + dim[2]//2, line_data[2]

            if not (line_data[3], line_data[4], line_data[5]) in color_to_ID:
                id = len(material_IDs)
                material_IDs[id] = np.array([line_data[3]/255, line_data[4]/255, line_data[5]/255], dtype='f4')
                color_to_ID[(line_data[3], line_data[4], line_data[5])] = id

            field[x][y][z] = 1
            materials[x][y][z] = color_to_ID[(line_data[3], line_data[4], line_data[5])]
            for x_i in range(-1, 1):
                for y_i in range(-1, 1):
                    for z_i in range(-1, 1):
                        if materials[x+x_i+1][y+y_i+1][z+z_i+1] == 5: materials[x+x_i+1][y+y_i+1][z+z_i+1] = color_to_ID[(line_data[3], line_data[4], line_data[5])]
            
            line = file.readline()

    return [field, materials]


def get_field_from_voxels_old(path, dim):
    field = np.zeros(shape=(dim)) - 1
    materials = np.zeros(shape=(dim[0] + 2, dim[1] + 2, dim[2] + 2))
    with open(f'voxelModels/{path}.ply', 'r') as file:
        while file.readline() != 'end_header\n':...
        line = file.readline()
        while line != '':
            line_data = list(map(int, line.split(' ')))
            x, z, y = line_data[0] + dim[0]//2, line_data[1] + dim[2]//2, line_data[2]
            field[x][y][z] = 1

            if not (line_data[3], line_data[4], line_data[5]) in color_to_ID:
                id = len(material_IDs)
                material_IDs[id] = np.array([line_data[3]/255, line_data[4]/255, line_data[5]/255], dtype='f4')
                color_to_ID[(line_data[3], line_data[4], line_data[5])] = id

            for x_mat in range(x, x + 2):
                if x_mat >= dim[0] + 2: continue
                for y_mat in range(y, y + 2):
                    if y_mat >= dim[1] + 2: continue
                    for z_mat in range(z, z + 2):
                        if z_mat >= dim[2] + 2: continue
                        materials[x_mat][y_mat][z_mat] = color_to_ID[(line_data[3], line_data[4], line_data[5])]
            line = file.readline()

    return [field, materials]

voxel_model_info = {
    'car' : (25, 25, 40),
    'castle' : (20, 20, 20),
    'chess' : (26, 10, 26),
    'wall' : (10, 10, 10),
    'room' : (20, 11, 20),
    'cottage' : (10, 10, 10),
    'room-eastdead' : (10, 10, 10),
    'room-northdead' : (10, 10, 10),
    'room-southdead' : (10, 10, 10),
    'room-westdead' : (10, 10, 10),
    'room-nshall' : (10, 10, 10),
    'room-wehall' : (10, 10, 10),
    'room-omnihall' : (10, 10, 10),
    'room-diner' : (20, 10, 20),
    'room-northstair' : (20, 20, 10),
    'room-biglibrary' : (30, 20, 30),
    'room-boss' : (30, 20, 30),
}

voxel_models = {
    model : get_field_from_voxels(model, voxel_model_info[model]) for model in voxel_model_info
}

def add_voxel_model_new(chunks: dict, model: str, pos: tuple):
    updated_chunks = []
    # Update feild
    for rel_x in range(voxel_model_info[model][0]):
        for rel_y in range(voxel_model_info[model][1]):
            for rel_z in range(voxel_model_info[model][2]):
                x, y, z = rel_x + pos[0], rel_y + pos[1], rel_z + pos[2]
                chunk_pos = (x//CHUNK_SIZE, y//CHUNK_SIZE, z//CHUNK_SIZE)
                chunk_rel_pos = (int(x%CHUNK_SIZE), int(y%CHUNK_SIZE), int(z%CHUNK_SIZE))
                chunk_key = f'{chunk_pos[0]};{chunk_pos[1]};{chunk_pos[2]}'
                if chunk_key not in chunks: continue
                chunk = chunks[chunk_key]
                chunk.field[chunk_rel_pos[0]][chunk_rel_pos[1]][chunk_rel_pos[2]] = voxel_models[model][0][rel_x][rel_y][rel_z]
                chunk.materials[chunk_rel_pos[0]][chunk_rel_pos[1]][chunk_rel_pos[2]] = voxel_models[model][1][rel_x][rel_y][rel_z]
                if not chunk in updated_chunks: updated_chunks.append(chunk)

    for chunk in updated_chunks:
        chunk.generate_mesh()

def add_voxel_model(chunks: dict, model: str, pos: tuple):
    updated_chunks = []
    # Update feild
    for rel_x in range(voxel_model_info[model][0]):
        for rel_y in range(voxel_model_info[model][1]):
            for rel_z in range(voxel_model_info[model][2]):
                x, y, z = rel_x + pos[0], rel_y + pos[1], rel_z + pos[2]
                chunk_pos = (x//CHUNK_SIZE, y//CHUNK_SIZE, z//CHUNK_SIZE)
                chunk_rel_pos = (int(x%CHUNK_SIZE), int(y%CHUNK_SIZE), int(z%CHUNK_SIZE))
                chunk_key = f'{chunk_pos[0]};{chunk_pos[1]};{chunk_pos[2]}'
                chunk = chunks[chunk_key]
                chunk.field[chunk_rel_pos[0]][chunk_rel_pos[1]][chunk_rel_pos[2]] = voxel_models[model][0][rel_x][rel_y][rel_z]

    # Update materials
    for rel_x in range(voxel_model_info[model][0]+1):
        for rel_y in range(voxel_model_info[model][1]+1):
            for rel_z in range(voxel_model_info[model][2]+1):
                x, y, z = rel_x + pos[0] - 1, rel_y + pos[1] - 1, rel_z + pos[2] - 1
                chunk_pos = (x//CHUNK_SIZE, y//CHUNK_SIZE, z//CHUNK_SIZE)
                chunk_rel_pos = (int(x%CHUNK_SIZE), int(y%CHUNK_SIZE), int(z%CHUNK_SIZE))
                chunk_key = f'{chunk_pos[0]};{chunk_pos[1]};{chunk_pos[2]}'
                chunk = chunks[chunk_key]
                chunk.materials[chunk_rel_pos[0]][chunk_rel_pos[1]][chunk_rel_pos[2]] = voxel_models[model][1][rel_x][rel_y][rel_z]
                if not chunk in updated_chunks: updated_chunks.append(chunk)

    return updated_chunks