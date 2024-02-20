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
        self.textures['cat'] = self.get_texture('objects/cat/20430_cat_diff_v1.jpg')
        self.textures['skybox'] = self.get_cubemap_texture('textures/skybox (2).png')
        self.textures['depth_texture'] = self.get_depth_texture()

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

    def get_cubemap_texture(self, dir):
        faces = [(2, 1), (0, 1), (1, 0), (1, 2)] + [(1, 1), (3, 1)][::-1]
        img = pg.image.load(dir).convert()
        texture_size = (img.get_rect()[2] / 4, img.get_rect()[3] / 3)
        
        textures = []
        for face in faces:
            texture = pg.Surface(texture_size)
            texture.blit(img, (-face[0] * texture_size[0], -face[1] * texture_size[1]))
            if face in [(2, 1), (0, 1), (1, 1), (3, 1)]:
                texture = pg.transform.flip(texture, True, False)
            else:
                texture = pg.transform.flip(texture, False, True)
            textures.append(texture)
            
        size = textures[0].get_size()
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)
        for i in range(6):
            texture_data = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def get_depth_texture(self):
        depth_texture = self.ctx.depth_texture(self.app.win_size)
        depth_texture.repeat_x = False
        depth_texture.repeat_y = False
        return depth_texture

    def destroy(self):
        [tex.release() for tex in self.textures.values()]