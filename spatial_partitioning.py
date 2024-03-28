import glm

class SpationalPartitionHandler():
    
    def __init__(self, object_handler, length = 16, dimensions = (10, 3, 10), pos = (0, 0, 0)):
        
        self.object_handler = object_handler
        self.partitions = {}
        self.dimensions = dimensions
        self.length = length
        self.pos = glm.vec3(pos)
        
        self.on_init()
        
    def on_init(self):
        
        # creates spatial partitions
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                for z in range(self.dimensions[2]):
                    
                    part_pos = self.pos + glm.vec3(x, y, z) * self.length
                    self.partitions[f'{x};{y};{z}'] = SpatialPartition(self, part_pos, self.length)
                    
        # populates partitions
        for obj in self.object_handler.objects:
            self.add_object(obj)
            
    def get_close_objects(self, obj):
        
        # gets object scale 8 4 2
        side_length = glm.length(obj.hitbox.dimensions)
        
        if side_length < 4: side_length = 4
        #elif side_length < 8: side_length = 4
        #elif side_length < 16: side_length = 8
        else: side_length = 16
        
        # gets all nearby objects from partitions of side length
        objects = set()
        vertices = self.get_int_vertices(obj)
        partitions = self.get_vertex_partitions(vertices)
        
        for key in partitions:
            objects = objects.union(self.partitions[key].get_close_objects(partitions[key], side_length))
        objects.discard(obj)
        return list(objects)
         
    def add_object(self, obj):
        
        vertices = self.get_int_vertices(obj)
        partitions = self.get_vertex_partitions(vertices)
        for key in partitions:
            self.partitions[key].add_object(obj, partitions[key])
        
    def get_vertex_partitions(self, vertices):
        
        partitions = {}
        for vertex in vertices:
            key = f'{int(vertex[0]//self.length)};{int(vertex[1]//self.length)};{int(vertex[2]//self.length)}'
            if key not in partitions: partitions[key] = []
            partitions[key].append(vertex)
        return partitions
        
    def get_int_vertices(self, obj):
        
        return [[int(i) for i in vertex] for vertex in obj.hitbox.vertices]
        
    def get_count(self):
        
        return sum([part.get_count() for part in self.partitions.values()])
    
    def remove_object(self, obj):
        
        for partition in self.partitions.values():
            if obj in partition.objs:
                partition.remove_object(obj)
        
class SpatialPartition():
    
    def __init__(self, spatial_partition_handler, pos, length):
        
        self.spatial_partition_handler = spatial_partition_handler
        self.pos = pos
        self.length = length
        self.objs = []
        self.partitions = {}
        
        if self.length > 4:
            self.on_init()
        
    def on_init(self):
        
        # create child partitions
        for offset in [[i, j, k] for k in range(2) for j in range(2) for i in range(2)]:
            pos = self.pos + glm.vec3(offset) * self.length
            self.partitions[f'{int(pos.x)};{int(pos.y)};{int(pos.z)}'] = SpatialPartition(self.spatial_partition_handler, pos, self.length // 4)
            
    def get_close_objects(self, vertices, side_length):
        
        # if in lowest testing area
        if self.length == side_length: 
            return set(self.objs)
        
        # gets lower testing objects
        objects = set()
        partitions = self.get_vertex_partitions(vertices)
        for key in partitions:
            objects = objects.union(self.partitions[key].get_close_objects(partitions[key], side_length))
        return objects
            
    def add_object(self, obj, vertices):
        
        self.objs.append(obj)
        
        # breaks if partition is a leaf
        if len(self.partitions) == 0: return
        
        partitions = self.get_vertex_partitions(vertices)
        for key in partitions:
            self.partitions[key].add_object(obj, partitions[key])
            
    def get_vertex_partitions(self, vertices):
        
        partitions = {}
        for vertex in vertices:
            key = f'{int(vertex[0]//self.length*self.length)};{int(vertex[1]//self.length*self.length)};{int(vertex[2]//self.length*self.length)}'
            if key not in partitions: partitions[key] = []
            partitions[key].append(vertex)
        return partitions
            
    def get_count(self):
        
        if len(self.partitions) == 0:
            return 1
        else:
            return sum([part.get_count() for part in self.partitions.values()])
        
    def remove_object(self, obj):
        
        self.objs.remove(obj)
        
        if len(self.partitions) == 0: return
        
        for partition in self.partitions.values():
            if obj in partition.objs:
                partition.remove_object(obj)
        
        