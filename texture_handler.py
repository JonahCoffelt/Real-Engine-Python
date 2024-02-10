import pygame as pg
import moderngl as mgl

class TextureHandler:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.textures = {}
        self.textures[0] = self.get_texture('textures/img.png')
        self.textures['container'] = self.get_texture('textures/container.png')
        self.textures['container_specular'] = self.get_texture('textures/container_specular.png')
        self.textures['metal_box'] = self.get_texture('textures/img_1.png')

    def get_texture(self, path):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, False, True)
        texture = self.ctx.texture(size=texture.get_size(), components=3,
                                   data = pg.image.tostring(texture, 'RGB'))
        # Mipmaps
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        # AF
        texture.anisotropy = 32.0

        return texture

    def destroy(self):
        [tex.release() for tex in self.textures.values()]