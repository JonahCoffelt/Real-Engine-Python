import glm
import pygame as pg
from config import config
import cudart


# Camera view constants
FOV = config['graphics']['FOV']  # Degrees
NEAR = 0.1
FAR = config['graphics']['far_plane_distance']

# Camera movement constants
SPEED = 0.01
SENSITIVITY = config['controls']['sensitivity'] / 10

class Camera:
    def __init__(self, app, position=(0, 3, 35), yaw=-90, pitch=0):
        self.app = app
        self.aspect_ratio = app.win_size[0] / app.win_size[1]
        # Position
        self.position = glm.vec3(position)
        # k vector for vertical movement
        self.UP = glm.vec3(0, 1, 0)
        # Movement vectors
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        # Look directions in degrees
        self.yaw = yaw
        self.pitch = pitch
        # View matrix
        self.m_view = self.get_view_matrix()
        # Projection matrix
        self.m_proj = self.get_projection_matrix()

        self.paused = False

    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def update_settings(self):
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

    def get_m_view(self):
        return self.m_view

    def rotate(self):
        """
        Rotates the camera based on the amount of mouse movement.
        """
        if not config['runtime']['simulate']: 
            self.paused = True
            return
        rel_x, rel_y = pg.mouse.get_rel()
        if self.paused:
            self.paused = False
            return
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        """
        Computes the forward vector based on the pitch and yaw. Computes horizontal and vertical vectors with cross product.
        """
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, self.UP))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def move(self):
        """
        Checks for button presses and updates vectors accordingly. 
        """
        if not config['runtime']['simulate']: return
        velocity = SPEED * self.app.delta_time
        keys = pg.key.get_pressed()
        if keys[config['controls']['forward']]:
            self.position += glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z)) * velocity
        if keys[config['controls']['backward']]:
            self.position -= glm.normalize(glm.vec3(self.forward.x, 0, self.forward.z)) * velocity
        if keys[config['controls']['left']]:
            self.position -= self.right * velocity
        if keys[config['controls']['right']]:
            self.position += self.right * velocity
        if keys[config['controls']['up']]:
            self.position += self.UP * velocity
        if keys[config['controls']['down']]:
            self.position -= self.UP * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
    
    def looking_at(self):
        
        looking_at = self.app.graphics_engine.scene.chunk_handler.ray_cast(test_start = 5)
        if looking_at is None: return self.forward
        return glm.normalize(looking_at - self.app.graphics_engine.scene.entity_handler.entities[0].obj.pos)
    
class FollowCamera(Camera):
    
    def __init__(self, app, followed, yaw=-90, pitch=0, radius = 4):
        
        self.followed = followed
        self.radius = radius
        self.look_point = glm.vec3(0, 0, 0)
        super().__init__(app, followed.pos, yaw, pitch)
        
    # follows object so no free cam movement
    def update(self):
        self.rotate()
        self.update_pos()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.look_point, self.up)
        
    def update_pos(self):
        
        # gets position of camera offset from player
        pos = [self.app.graphics_engine.scene.entity_handler.entities[0].obj.pos[i] + [0, 0.5, 0][i] for i in range(3)]
        
        back_location = self.app.graphics_engine.scene.chunk_handler.ray_cast_vec(pos, -self.forward + self.up + self.right, multiplier = 1/20, starting_test = 2, tests = 20)
        if back_location is not None: 
            self.look_point = back_location
        else: self.look_point = pos -self.forward + self.up + self.right
        
        # draws vector backwards to nearest wall
        back_location = self.app.graphics_engine.scene.chunk_handler.ray_cast_vec(self.look_point, -self.forward, multiplier = self.radius/100, starting_test = 20, tests = 100)
        if back_location is not None: 
            self.position = back_location
            return
        self.position = self.look_point - self.forward * self.radius
        
    def rotate(self):
        """
        Rotates the camera based on the amount of mouse movement.
        """
        if not config['runtime']['simulate']: 
            self.paused = True
            return
        rel_x, rel_y = pg.mouse.get_rel()
        if self.paused:
            self.paused = False
            return
        self.yaw += rel_x * SENSITIVITY
        self.pitch -= rel_y * SENSITIVITY
        self.pitch = max(-89, min(89, self.pitch))