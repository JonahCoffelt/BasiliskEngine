from scripts.camera import Camera
from scripts.vao_handler import VAOHandler
from scripts.object_handler import ObjectHandler


class Scene:
    def __init__(self, engine, project) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine and project
        self.engine = engine
        self.project = project
        # Stores the ctx
        self.ctx = self.engine.ctx

        self.time = 0

        # Makes a free cam
        self.camera = Camera(self.engine)

        # Gets handlers from parent project
        self.vao_handler = self.project.vao_handler
        self.object_handler = ObjectHandler(self)
        
        # Used to incorperate the scene into the render pipline. Allows for scene switching within projects
        self.use_scene()

        for x in range(20):
            for y in range(20):
                for z in range(20):
                    self.object_handler.add_object('cube', position=(x * 4, y * 4, z * 4))
        
    def use_scene(self):
        self.vao_handler.shader_handler.set_camera(self.camera)
        self.vao_handler.shader_handler.write_all_uniforms()

    def update(self):
        """
        Updates dynamic objects, uniforms, and camera
        """

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