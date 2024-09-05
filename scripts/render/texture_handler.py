import pygame as pg
import numpy as np
import moderngl as mgl
import os


class TextureHandler:
    def __init__(self, engine, vao_handler, directory: str='textures') -> None:
        # Stores the engine and context
        self.engine = engine
        self.vao_handler = vao_handler
        self.ctx = self.engine.ctx

        # The folder containing all textures for the project
        self.directory = directory

        # Dictionary containing all texture's data. This is not the texture itself.
        self.textures = {}
        self.texture_ids = {}

        # Dictionary containing all texture arrays
        self.sizes = (128, 256, 512, 1024, 2048)
        self.texture_arrays = {size : [] for size in self.sizes}

        # Load all textures
        self.load_directory()

    def write_textures(self, program='default') -> None:
        program = self.vao_handler.shader_handler.programs[program]
        for i, size in enumerate(self.sizes):
            if not size in self.texture_arrays: continue
            program[f'textureArrays[{i}].array'] = i + 3
            self.texture_arrays[size].use(location=i+3)

    def generate_texture_arrays(self):
        size_data = {size : [] for size in self.sizes}
        self.texture_ids.clear()

        for texture in self.textures:
            data = self.textures[texture][0].read()
            size = self.textures[texture][1]
            location = (self.sizes.index(size), len(size_data[size]))

            size_data[size].append(data)
            self.texture_ids[texture] = location

        for size in self.sizes:
            data = np.array(size_data[size])
            self.texture_arrays[size] = self.ctx.texture_array((size, size, len(size_data[size])), 3, data)
            # Mipmaps
            self.texture_arrays[size].build_mipmaps()
            self.texture_arrays[size].filter = (mgl.NEAREST_MIPMAP_NEAREST, mgl.NEAREST)
            # AF
            self.texture_arrays[size].anisotropy = 32.0

    def load_texture(self, name: str, file: str) -> None:
        """
        Loads a texture in the project texture directory.
        If no directory was given on init, full path is expected in the file argument.
        File argument should include the file extension.
        """

        # Constructs the path based on file and directory
        if self.directory: path = self.directory + file
        else: path = file

        # Loads image using pygame
        texture = pg.image.load(path).convert()

        # Get the closest size
        original_size = texture.get_size()[0]
        distances = np.array([abs(bucket_size - original_size) for bucket_size in self.sizes])
        size = self.sizes[np.argmin(distances)]

        # Rescale to closest size bucket
        texture = pg.transform.scale(texture, (size, size))
        texture = pg.transform.flip(texture, False, True)

        # Make a texture
        texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))

        self.textures[file[1:-4]] = (texture, size)

    def load_directory(self):
        for file in os.listdir(self.directory):
            file = '/' + file
            self.load_texture(file, file)
        
        self.generate_texture_arrays()
        self.write_textures()

    def release(self) -> None:
        """
        Releases all textures in a project
        """

        [tex.release() for tex in self.textures.values()]