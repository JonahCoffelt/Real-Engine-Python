import numpy as np
from scripts.object import Object

CHUNK_SIZE = 40


class ObjectHandler:
    def __init__(self, scene) -> None:
        # Reference to the scene hadlers and variables
        self.scene =       scene
        self.ctx   =       scene.ctx
        self.vbos  =       scene.vao_handler.vbo_handler.vbos
        self.program =     scene.vao_handler.shader_handler.programs['batch']
        self.texture_ids = scene.project.texture_handler.texture_ids

        self.view_distance = 4  # In chunks

        self.objects = []  # List containig all objects
        self.chunks  = {}  # Contain lists with objects positioned in a bounding box in space (Spatial partitioning)
        self.batches = {}  # Contains VBOs for the chunk meshes

        self.updated_chunks = set()  # Chunks that need to have their mesh updated on the next frame

    def render(self) -> None:
        """
        Renders all the chunk batches in the camera's range
        Includes some view culling, but not frustum culling. 
        """
        
        # Gets a rectanglur prism of chunks in the cameras view
        render_range_x, render_range_y, render_range_z = self.get_render_range()

        # Loop through all chunks in view and render
        for x in range(*render_range_x):
            for y in range(*render_range_y):
                for z in range(*render_range_z):
                    chunk = (x, y, z)  # Key of the chunk
                    
                    if chunk not in self.batches: continue  # Dont render non-existent chunks

                    self.batches[chunk][1].render()

    def update(self) -> None:           
        """
        Batches all the chunks that have been updated since the last frame. 
        """ 
        # Loop through the set of updated chunk keys and batch the chunk
        for chunk in self.updated_chunks:
            self.batch_chunk(chunk)

        # Clears the set of updated chunks so that they are batched unless they are updated again
        self.updated_chunks.clear()

    def batch_chunk(self, chunk_key: tuple) -> None:
        """
        Combines all the verticies of the chunk's objects into a single VBO.
        This mesh can render the whole chunk in just on render call.
        Args:
            chunk_key: tuple = (x, y, z)
                The position of the chunk. Used as the key in the chunks and batches dicts
        """
        
        # Get the chunks from key
        chunk = self.chunks[chunk_key]

        # Empty list to contain all vertex data of objects in the chunk
        batch_data = []

        # Loop through each object in the chunk, adding the object's mesh to batch_data
        for object in chunk:
            # Get all needed information from the vbo and the object
            vertex_data = np.copy(self.vbos[object.vbo].vertex_data)
            model_data = np.array([*object.position, *object.rotation, *object.scale, *object.texture])

            # Create an empty array to hold the object's mesh data
            object_data = np.zeros(shape=(vertex_data.shape[0], 19), dtype='f4')

            # Add the vbo and object information to the mesh
            object_data[:,:8] = vertex_data
            object_data[:,8:] = model_data

            # Store the mesh
            batch_data.append(object_data)

        # Combine all meshes into a single array
        if len(batch_data) > 1: batch_data = np.vstack(batch_data)
        else: batch_data = np.array(batch_data, dtype='f4')

        # If there are no verticies, delete the chunk
        if len(batch_data) == 0:
            if chunk_key in self.batches: del self.batches[chunk_key]
            if chunk_key in self.chunks: del self.chunks[chunk_key]
            return

        # Release any existing vbo and vaos for the chunk
        if chunk_key in self.batches:
            self.batches[chunk_key][0].release()
            self.batches[chunk_key][1].release()

        # Create the vbo and the vao from mesh data
        vbo = self.ctx.buffer(batch_data)
        vao = self.ctx.vertex_array(self.program, [(vbo, '3f 2f 3f 3f 3f 3f 2f', *['in_position', 'in_uv', 'in_normal', 'obj_position', 'obj_rotation', 'obj_scale', 'obj_texture'])], skip_errors=True)

        # Store batched chunk mesh in the batches dict
        self.batches[chunk_key] = (vbo, vao)

    def get_render_range(self) -> tuple:
        """
        Returns a rectangluar prism of chunks that are in the camera's view.
        Tuple return is in form ((x1, x2), (y1, y2), (z1, z2))
        """
        
        cam_position = self.scene.camera.position  # glm.vec3(x, y, z)
        fov = 40  # The range in which a direction will not be culled

        # Default to a cube of chunks around the camera extending view_distance chunks in each direction
        render_range_x = [int(cam_position.x // CHUNK_SIZE - self.view_distance), int(cam_position.x // CHUNK_SIZE + self.view_distance + 1)]
        render_range_y = [int(cam_position.y // CHUNK_SIZE - self.view_distance), int(cam_position.y // CHUNK_SIZE + self.view_distance + 1)]
        render_range_z = [int(cam_position.z // CHUNK_SIZE - self.view_distance), int(cam_position.z // CHUNK_SIZE + self.view_distance + 1)]

        # Remove chunks that the play is facing away from
        render_range_x[1] -= self.view_distance * (180 - fov < self.scene.camera.yaw < 180 + fov) - 1
        render_range_x[0] += self.view_distance * (-fov < self.scene.camera.yaw < fov or self.scene.camera.yaw > 360 - fov) - 1

        render_range_y[0] += self.view_distance * (self.scene.camera.pitch > 25) - 1
        render_range_y[1] -= self.view_distance * (self.scene.camera.pitch < -25) - 1

        render_range_z[1] -= self.view_distance * (270 - fov < self.scene.camera.yaw < 270 + fov) - 1
        render_range_z[0] += self.view_distance * (90 - fov < self.scene.camera.yaw < 90 + fov) - 1


        return (render_range_x, render_range_y, render_range_z)

    def add(self, vbo: str="cube", texture: str="box", position: tuple=(0, 0, 0), rotation: tuple=(0, 0, 0), scale: tuple=(1, 1, 1)) -> Object:
        """
        Add an object to the scene.
        Returns the object instance.
        Args:
            vbo: str="cube":
                The key of the vbo that the object will have. This is the object's model
            texture: str="box":
                Name of the objects texture. Will be name of texture file (w/o extension)
            position: tuple=(x, y, z):
                Initial position of the object
            rotation: tuple=(x-axis, y-axis, z-axis):
                Rotation of the object on each axis in radians
            scale: tuple=(x_scale, y_scale, z_scale):
                The length of the object in each direction
        """

        # The key of the chunk the object will be added to
        chunk = (position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE)

        # Create empty list if the chunk does not already exist
        if chunk not in self.chunks:
            self.chunks[chunk] = []

        # Create a new object from the given parameters
        new_object = Object(self, vbo, self.texture_ids[texture], position, rotation, scale)

        # Add the object to the objects list and to its correct chunk list
        self.objects.append(new_object)
        self.chunks[chunk].append(new_object)
        self.updated_chunks.add(chunk)

        return new_object

    def remove(self, object) -> None:
        """
        Removes an object from the scene
        """

        chunk = object.chunk
        self.objects.remove(object)
        self.chunks[chunk].remove(object)

        self.updated_chunks.add(chunk)

        del object