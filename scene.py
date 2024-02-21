from object_handler import ObjectHandler
from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler
import numpy as np
import glm

class Scene:
    def __init__(self, graphics_engine) -> None:
        self.graphics_engine = graphics_engine
        self.ctx = graphics_engine.ctx

        self.vao_handler = VAOHandler(self.ctx)
        self.texture_handler = TextureHandler(self.graphics_engine.app)
        self.light_handler = LightHandler()
        self.objects = ObjectHandler(self)

        # Depth buffer
        self.depth_texture = self.texture_handler.textures['depth_texture']
        self.depth_fbo = self.ctx.framebuffer(depth_attachment=self.depth_texture)

        self.shadow_timer = 5
        self.shadow_frame_skips = 5

        self.time = 0

    def render_main(self):
        self.ctx.screen.use()
        self.objects.render()

    def render_shadow(self):
        self.depth_fbo.clear()
        self.depth_fbo.use()
        self.objects.render_shadows()

    def render(self):
        # Update
        self.time += self.graphics_engine.app.delta_time
        self.light_handler.dir_light.color = glm.vec3(np.array([1, 1, 1]) - np.array([.8, .9, .6]) * (min(.75, max(.25, (np.sin(self.time / 500)*.5 + .5))) * 2 - .5))
        self.objects.update()
        # Pass 1
        if self.shadow_timer // self.shadow_frame_skips:
            self.render_shadow()
            self.shadow_timer = 0
        else:
            self.shadow_timer += 1
        # Pass 2
        self.render_main()