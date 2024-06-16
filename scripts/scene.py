import pygame as pg
import random
from scripts.camera import Camera
from scripts.object_handler import ObjectHandler
from scripts.light_handler import LightHandler


class Scene:
    def __init__(self, engine, project) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine, project, and ctx
        self.engine = engine
        self.project = project
        self.ctx = self.engine.ctx
        self.timer = 0

        # Makes a free cam
        self.camera = Camera(self.engine)

        # Gets handlers from parent project
        self.vao_handler = self.project.vao_handler

        # Creates handlers for the scene
        self.object_handler = ObjectHandler(self)
        self.light_handler = LightHandler()

        self.add_grid(20, 4)

        
    def add_grid(self, size, spacing=4):
        mats = ('box', 'metal_box', 'crate')
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    mat = mats[random.randrange(0, 3)]
                    self.object_handler.add_object(mat, position=(x * spacing, y * spacing, z * spacing), rotation=(0, 0, 0))

    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.project.render_handler.generate_g_buffer()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.texture_handler.write_textures(self.vao_handler.shader_handler.programs['g_buffer'])

    def update(self):
        """
        Updates uniforms, and camera
        """

        if self.engine.keys[pg.K_UP]:
            self.object_handler.objects[0].data[0] += 5 * self.engine.dt
        if self.engine.keys[pg.K_DOWN]:
            self.object_handler.objects[0].data[0] -= 5 * self.engine.dt
        if self.engine.keys[pg.K_LEFT]:
            self.object_handler.objects[0].data[2] += 5 * self.engine.dt
        if self.engine.keys[pg.K_RIGHT]:
            self.object_handler.objects[0].data[2] -= 5 * self.engine.dt

        if self.engine.keys[pg.K_r]:
            self.object_handler.remove_object(self.object_handler.objects[0])
        
        self.object_handler.update()
        self.vao_handler.shader_handler.update_uniforms()
        self.light_handler.write(self.vao_handler.vaos['frame'].program)
        self.camera.update()

    def render(self):
        """
        Redners all instances
        """

        #self.ctx.screen.use()
        self.project.render_handler.use()

        self.object_handler.render()

        self.project.render_handler.render()


    def release(self):
        """
        Releases scene's VAOs
        """

        self.vao_handler.release()