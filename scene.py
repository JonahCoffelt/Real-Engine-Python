from object_handler import ObjectHandler
from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler

class Scene:
    def __init__(self, graphics_engine) -> None:
        self.graphics_engine = graphics_engine
        self.ctx = graphics_engine.ctx

        self.vao_handler = VAOHandler(self.ctx)
        self.texture_handler = TextureHandler(self.ctx)
        self.objects = ObjectHandler(self)
        self.light_handler = LightHandler()

    def render_main(self):
        self.objects.render()

    def render_shadow(self): ... 

    def render(self):
        # Pass 1
        self.render_shadow()
        # Pass 2
        self.render_main()