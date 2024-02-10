from object_handler import ObjectHandler
from vao_handler import VAOHandler
from texture_handler import TextureHandler
from light_handler import LightHandler

class Scene:
    def __init__(self, app, graphics_engine) -> None:
        self.app = app
        self.graphics_engine = graphics_engine
        self.ctx = app.ctx

        self.vao_handler = VAOHandler(self.app)
        self.texture_handler = TextureHandler(self.app)

        self.objects = ObjectHandler(self)
        self.particles = None
        self.light_handler = LightHandler()

    def render_main(self):
        for program in self.vao_handler.program_handler.programs.values():
            self.light_handler.write(program)
        self.objects.render()

    def render_shadow(self): ... 

    def render(self):
        # Pass 1
        self.render_shadow()
        # Pass 2
        self.render_main()