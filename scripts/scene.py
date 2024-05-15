from scripts.camera import Camera
from scripts.object_handler import ObjectHandler
import random

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
        self.object_handler = ObjectHandler(self)

        mats = ('cube', 'metal_box', 'crate')

        for x in range(-15, 15):
            for y in range(3):
                for z in range(-15, 15):
                        mat = mats[random.randrange(0, 3)]
                        self.object_handler.add_object(mat, position=(x * 4, y * 8, z * 4))
        
    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.project.render_handler.generate_g_buffer()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.texture_handler.write_textures(self.vao_handler.shader_handler.programs['g_buffer'])
        self.object_handler.use()

    def update(self):
        """
        Updates uniforms, and camera
        """
        self.timer += self.engine.dt
        if self.timer > 16:
            self.object_handler.construct_data()
            self.timer = 0
        self.vao_handler.shader_handler.update_uniforms()
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