import numpy as np
import random
import glm
from data.config import config
#import cudart


class Atmosphere:
    def __init__(self, scene):
        self.scene = scene
        self.sky_program = scene.vao_handler.program_handler.programs['skybox']
        self.dir_light = scene.light_handler.dir_light

        self.sky_program['FOV'].write(glm.float32(config['graphics']['FOV']))
        self.sky_program['aspectRatio'].write(glm.float32(config['graphics']['aspect_ratio']))

        self.stars = np.array([[random.uniform(0, 360), random.uniform(105, 140), random.uniform(15, 30)/10000] for i in range(40)], dtype='f4')

        self.time = 0
        self.sky_colors = {
            3 :  np.array([[0, 17, 127],   [0, 63, 132],      [0, 109, 137] ,  [30, 109, 137]],  dtype='f4'), # Night end, sunrise begin
            6 :  np.array([[0, 114, 130],  [130, 137.5, 93],  [240, 161, 56],  [240, 161, 56]],  dtype='f4'), # Sunrise
            11 : np.array([[59, 147, 255], [87, 162.5, 255],  [115, 178, 255], [255, 255, 255]], dtype='f4'), # Day
            16 : np.array([[59, 147, 255], [87, 162.5, 255],  [115, 178, 255], [255, 255, 255]], dtype='f4'), # Day end, sunset begin
            19 : np.array([[0, 23, 145],   [92.5, 51.5, 140], [185, 80, 135],  [185, 80, 135]],  dtype='f4'), # Sunset
            22 : np.array([[0, 17, 127],   [0, 63, 132],      [0, 109, 137] ,  [30, 109, 137]],  dtype='f4'), # Night
        }
        self.sky_colors = {
            0 :  np.array([[0, 17, 127],   [0, 63, 132],      [0, 109, 137] ,  [125, 125, 125]],  dtype='f4'), # Night end, sunrise begin
            23 : np.array([[0, 17, 127],   [0, 63, 132],      [0, 109, 137] ,  [125, 125, 150]],  dtype='f4'), # Night
        }
        self.times = np.array(list(self.sky_colors.keys()))


        dawn_color_1 = np.array([0, 17, 127], dtype='f4') / 255
        dawn_color_3 = np.array([0, 114, 138], dtype='f4') / 255
        dawn_color_2 = (dawn_color_1 + dawn_color_3) / 2

        self.sky_program[f'color1'].write(glm.vec3(*dawn_color_1))
        self.sky_program[f'color2'].write(glm.vec3(*dawn_color_2))
        self.sky_program[f'color3'].write(glm.vec3(*dawn_color_3))

        for i, star in enumerate(self.stars):
            self.sky_program[f'stars[{i}].x'].write(glm.float32(star[0]))
            self.sky_program[f'stars[{i}].y'].write(glm.float32(star[1]))
            self.sky_program[f'stars[{i}].s'].write(glm.float32(star[2]))

    def update(self, dt):
        self.time += dt
        self.time = self.time % 24
        time_index = np.searchsorted(self.times, self.time)


        t1, t2 = self.times[time_index - 1], self.times[time_index%len(self.sky_colors)]
        color1, color2 = self.sky_colors[t1], self.sky_colors[t2]

        color = (color2 - color1) / (t2 - t1) * (self.time - t1) + color1

        self.sky_program[f'time'].write(glm.float32(self.time))
        self.sky_program[f'color1'].write(color[0] / 255)
        self.sky_program[f'color2'].write(color[1] / 255)
        self.sky_program[f'color3'].write(color[2] / 255)

        self.dir_light.color = color[3] / 255


    def render(self):
        self.scene.object_handler.render('skybox', light=False, object_types=('skybox'))
