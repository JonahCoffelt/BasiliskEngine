import pygame as pg
import numpy as np
from scripts.camera import Camera
from scripts.object_handler import ObjectHandler
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

        spacing = 6

        models = ['cube', 'cow']

        for x in range(0, 5):
            for y in range(0, 5):
                for z in range(0, 5):
                    self.object_handler.add(models[randrange(0, 2)], "cow", (x * spacing, y * spacing, z * spacing), (0, 0, 0), (1, 1, 1))

        self.selected_object = self.object_handler.add("cow", "box", (x * spacing, y * spacing, z * spacing), (0, 0, 0), (3, 3, 3))

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