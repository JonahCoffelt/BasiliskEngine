from scripts.camera import Camera
from scripts.object_handler import ObjectHandler


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
        self.object_handler = ObjectHandler(self)
        
    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.object_handler.use()

    def update(self):
        """
        Updates uniforms, and camera
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