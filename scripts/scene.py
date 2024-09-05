import pygame as pg
import numpy as np
from scripts.camera import Camera
from scripts.object_handler import ObjectHandler
from scripts.collisions.collider_handler import ColliderHandler
from scripts.physics.physics_body_handler import PhysicsBodyHandler
from scripts.collections.collection_handler import *
from scripts.skeletons.skeleton_handler import SkeletonHandler
import glm
from random import uniform, randrange




class Scene:
    def __init__(self, engine, project) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine, project, and ctx
        self.engine = engine
        self.project = project
        self.ctx = self.engine.ctx

        # Makes a free cam
        self.camera = Camera(self.engine)

        # Gets handlers from parent project
        self.vao_handler = self.project.vao_handler
        # Object handler
        self.object_handler = ObjectHandler(self)
        self.collider_handler = ColliderHandler(self)
        self.physics_body_handler = PhysicsBodyHandler(self)
        self.collection_handler = CollectionHandler(self)
        self.skeleton_handler = SkeletonHandler(self)

        spacing = 6

        models = ['cube', 'cow']

        '''for x in range(0, 5):
            for y in range(0, 5):
                for z in range(0, 5):
                    self.object_handler.add(models[randrange(0, 2)], "cow", (x * spacing, y * spacing, z * spacing), (0, 0, 0), (1, 1, 1))'''

        self.selected_object = self.object_handler.add("cow", "box", (4 * spacing, 4 * spacing, 4 * spacing), (0, 0, 0), (3, 3, 3))
        
        for x in range(2):
            for y in range(6):
                for z in range(2):
                    self.collection_handler.add_single(
                        position= (x * 4 -2, y * 4 + 5, z * 4 -2),
                        rotation=(0, 0, 0),
                        scale=(1, 1, 1),
                        object=self.object_handler.add('cube'),
                        physics_body=self.physics_body_handler.add_physics_body(mass=20),
                        collider=self.collider_handler.add_collider(vbo='cube', static=False),
                        name='cube'
                    )
        
        # temp, adds base plate
        if True:
            self.collection_handler.add_collection(
                position=(0, 0, 0),
                scale=(1, 1, 1),
                rotation=(0, 0, 0),
                collections=[
                    self.collection_handler.create_single(
                        position=glm.vec3(0, -4, 0), 
                        scale=(10, 1, 10),
                        rotation=(0, 0, 0),
                        object=self.object_handler.add('cube', 'cow'), 
                        collider=self.collider_handler.add_collider(vbo='cube'),
                        name='bowl side'
                        ),
                    self.collection_handler.create_single(
                        position=glm.vec3(0, -2.1, 10), 
                        scale=(10, 1, 5), 
                        rotation=(glm.pi()/9, 0, 0),
                        object=self.object_handler.add('cube', 'metal'), 
                        collider=self.collider_handler.add_collider(),
                        name='bowl side'
                        ),
                    self.collection_handler.create_single(
                        position=glm.vec3(0, -2.1, -10),
                        scale=(10, 1, 5),
                        rotation=(-glm.pi()/9, 0, 0),
                        object=self.object_handler.add('cube', 'metal'), 
                        collider=self.collider_handler.add_collider(vbo='cube'),
                        name='bowl side'
                        ),
                    self.collection_handler.create_single(
                        position=glm.vec3(10, -2.1, 0), 
                        scale=(5, 1, 10), 
                        rotation=(0, 0, -glm.pi()/9),
                        object=self.object_handler.add('cube', 'metal'), 
                        collider=self.collider_handler.add_collider(vbo='cube'),
                        name='bowl side'
                        ),
                    self.collection_handler.create_single(
                        position=glm.vec3(-10, -2.1, 0), 
                        scale=(5, 1, 10), 
                        rotation=(0, 0, glm.pi()/9),
                        object=self.object_handler.add('cube', 'metal'), 
                        collider=self.collider_handler.add_collider(vbo='cube'),
                        name='bowl side'
                        )
                ], 
                name='bowl')
            
        self.collider_handler.construct_bvh()
                
    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.texture_handler.write_textures()
        self.project.texture_handler.write_textures('batch')

    def update(self):
        """
        Updates uniforms, and camera
        """
        
        if self.engine.keys[pg.K_e]:
            place_range = 100
            for i in range(100):
                self.object_handler.add(position=(self.camera.position.x + randrange(-place_range, place_range), self.camera.position.y + randrange(-place_range, place_range), self.camera.position.z + randrange(-place_range, place_range)))
        
        self.selected_object.scale.x += (self.engine.keys[pg.K_UP] - self.engine.keys[pg.K_DOWN]) * self.engine.dt * 10
        self.selected_object.scale.z += (self.engine.keys[pg.K_RIGHT] - self.engine.keys[pg.K_LEFT]) * self.engine.dt * 10

        self.object_handler.update()
        self.vao_handler.shader_handler.update_uniforms()
        self.camera.update()


    def render(self):
        """
        Redners all instances
        """

        self.ctx.screen.use()
        self.object_handler.render()

    def release(self):
        """
        Releases scene's VAOs
        """

        self.vao_handler.release()
        
        
    def get_hovered(self):
        """
        gets the closest collection tree or object to the mouse. Returns none if nothing is close.
        """
        best_name, distance = None, 1e10
        # checks collections
        mouse_position = glm.vec2(*self.engine.mouse_position)
        for collection in self.collection_handler.collections:
            names, objects = collection.get_objects_with_path()
            for index, object in enumerate(objects):
                if glm.dot(object.data[:3] - self.camera.position, self.camera.forward) <= 0: continue # moves on if object is behind screen
                matrix = self.collider_handler.get_model_matrix(object.data)
                for triangle in self.project.prefab_handler.prefabs[object.prefab].triangles:
                     # Project vertices and check if they're in front of the camera
                    points = []
                    behind_camera = False
                    for i in range(3):
                        vertex = glm.vec4(triangle[i], 1.0)
                        clip_space = self.camera.m_proj * self.camera.m_view * matrix * vertex
                        
                        # If the vertex is behind the near plane, mark it and break
                        if clip_space.z <= -clip_space.w:
                            behind_camera = True
                            break
                        
                        # Otherwise, add the projected vertex to points
                        points.append(self.project_vertex(matrix, triangle[i]))
                    
                    # skip triangles with vertices behind the camera
                    if behind_camera: continue
                    # check if mouse position is in face
                    v = [p - points[2] for p in [points[0], points[1], mouse_position]]
                    dot00, dot01, dot02, dot11, dot12 = glm.dot(v[0], v[0]), glm.dot(v[0], v[1]), glm.dot(v[0], v[2]), glm.dot(v[1], v[1]), glm.dot(v[1], v[2])
                    determinant = (dot00 * dot11 - dot01 * dot01)
                    if abs(determinant) < 1e-8: continue
                    inv = 1 / determinant
                    u = (dot11 * dot02 - dot01 * dot12) * inv
                    v = (dot00 * dot12 - dot01 * dot02) * inv
    
                    # check if point is in the triangle
                    if u >= 0 and v >= 0 and u + v <= 1 and glm.length(object.data[:3] - self.camera.position) < distance: 
                        best_name = names[index]
                        break
        print(best_name)
        
    def project_vertex(self, matrix:glm.mat4, vertex:glm.vec3|list) -> list:
        """
        projects a vertex in the world space onto the clip plane
        """
        # get projection
        clip_space = self.camera.m_proj * self.camera.m_view * matrix * glm.vec4(vertex, 1.0)
        ndc = glm.vec3(clip_space) / clip_space.w
        # get pixel position
        x = int((ndc.x + 1) * 0.5 * self.engine.win_size[0])
        y = int((1 - ndc.y) * 0.5 * self.engine.win_size[1])
        return glm.vec2(x, y)