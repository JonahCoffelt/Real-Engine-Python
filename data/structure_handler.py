from data.voxel_marching_cubes_construct import add_voxel_model

# model : model_name
# lights : ((x, y, z), (idk), idk)
# particles : (type, (x, y, z), idk)
# entities : ((x, y, z), square_radius, probability)

structures = {
    'chess' : {'model' : 'chess', 'lights' : [], 'particles' : [], 'entities' : []},
    'hub' : {'model' : 'hub','lights' : [], 'particles' : [], 'entities' : []},
    'basic_room' : {
        'model' : 'room',
        'lights' : [
            ((4, 4, 4), (1.0, .7, .3), 3.0),
            ((16, 4, 4), (1.0, .7, .3), 3.0),
            ((4, 4, 16), (1.0, .7, .3), 3.0),
            ((16, 4, 16), (1.0, .7, .3), 3.0)
        ],
        'particles' : [
            ('fire', (4, 4, 4), None),
            ('fire', (16, 4, 4), None),
            ('fire', (4, 4, 16), None),
            ('fire', (16, 4, 16), None)
        ],
        'entities' : [

        ]
    },
    # single chunk dead end halls and connector hall
    'room-eastdead' : {'model' : 'room-eastdead', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-northdead' : {'model' : 'room-northdead', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-omnihall' : {'model' : 'room-omnihall', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-southdead' : {'model' : 'room-southdead', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-westdead' : {'model' : 'room-westdead', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-nshall' : {'model' : 'room-nshall', 'lights' : [((5, 4, 3), (1.0, .7, .3), 2.0), ((5, 4, 6), (1.0, .7, .3), 2.0)], 'particles' : [('fire', (5, 4, 3), None), ('fire', (5, 4, 6), None)], 'entities' : []},
    'room-wehall' : {'model' : 'room-wehall', 'lights' : [((3, 4, 5), (1.0, .7, .3), 2.0), ((6, 4, 5), (1.0, .7, .3), 2.0)], 'particles' : [('fire', (3, 4, 5), None), ('fire', (6, 4, 5), None)], 'entities' : []},

    # basic stairs
    'room-northstair' : {'model' : 'room-northstair', 'lights' : [], 'particles' : [], 'entities' : []},
    
    # dungeon rooms
    'room-basic1' : {'model' : 'room-basic1', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-basic2' : {'model' : 'room-basic2', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-tall1' : {'model' : 'room-tall1', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-spawn' : {'model' : 'room-northdead', 'lights' : [], 'particles' : [], 'entities' : []},
    'room-diner' : {'model' : 'room-diner', 'lights' : [], 'particles' : [], 
        'entities' : [
            ((10, 3, 10), 5, 1)
        ]},
    'room-biglibrary' : {'model' : 'room-biglibrary', 'lights' : [], 'particles' : [], 
        'entities' : [
            ((15, 3, 15), 5, 1)
        ]},
    'room-boss' : {'model' : 'room-boss', 
        'lights' : [
                ((14.5, 9, 24), 5, 1),
                ((5, 9, 24), 5, 1),
                ((24, 9, 24), 5, 1),
                ((24, 9, 14.5), 5, 1),
                ((24, 9, 5), 5, 1),
                ((14.5, 9, 5), 5, 1),
                ((5, 9, 5), 5, 1),
            ], 
        'particles' : [
                ('fire', (14.5, 9, 24), None),
                ('fire', (5, 9, 24), None),
                ('fire', (24, 9, 24), None),
                ('fire', (24, 9, 14.5), None),
                ('fire', (24, 9, 5), None),
                ('fire', (14.5, 9, 5), None),
                ('fire', (5, 9, 5), None),
            ], 
        'entities' : []},
}

class StructureHandler:
    def __init__(self, chunk_handler, light_handler, particle_emitter_handler):
        self.chunk_handler = chunk_handler
        self.chunks = chunk_handler.chunks
        self.light_handler = light_handler
        self.particle_emitter_handler = particle_emitter_handler

        self.add_structure('basic_room', (2, 3, 2))
        self.add_structure('basic_room', (27, 3, 2))
        self.add_structure('basic_room', (2, 3, 27))
        self.add_structure('basic_room', (27, 3, 27))

    def add_structure(self, structure_key: str, pos: tuple):
        # Fetch the structure dict
        structure = structures[structure_key]
        # Update the chunks with the model
        updated_chunks = add_voxel_model(self.chunks, structure['model'], pos)
        # Add all lights at relative positions
        for light in structure['lights']:
            light_pos = light[0]
            light_pos = (light_pos[0] + pos[0], light_pos[1] + pos[1], light_pos[2] + pos[2])
            self.light_handler.add_light(light_pos, light[1], light[2])
        for emitter in structure['particles']:
            emitter_pos = emitter[1]
            emitter_pos = (emitter_pos[0] + pos[0], emitter_pos[1] + pos[1], emitter_pos[2] + pos[2])
            self.particle_emitter_handler.add_emitter(template=emitter[0], pos=emitter_pos, particle_attribs=emitter[2])

        return updated_chunks
