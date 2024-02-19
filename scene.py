from object_handler import ObjectHandler
from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler

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

    def render_main(self):
        self.ctx.screen.use()
        self.objects.render()

    def render_shadow(self):
        self.depth_fbo.clear()
        self.depth_fbo.use()
        self.objects.render_shadows()

    def render(self):
        # Pass 1
        self.render_shadow()
        # Pass 2
        self.render_main()