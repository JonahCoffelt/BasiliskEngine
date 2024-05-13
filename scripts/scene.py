from scripts.camera import Camera
from scripts.vao_handler import VAOHandler
from scripts.object_handler import ObjectHandler


class Scene:
    def __init__(self, engine) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine
        self.engine = engine
        self.simulation_time = 0
        # Stores the ctx
        self.ctx = self.engine.ctx

        # Makes a free cam
        self.camera = Camera(self.engine)

        # Creats all necessary handlers
        self.vao_handler = VAOHandler(self)
        self.vao_handler.shader_handler.write_all_uniforms()
        self.object_handler = ObjectHandler(self)
        self.object_handler.add_object('cube', position=(-10, 0, -10), scale=(20, 1, 20))
        self.object_handler.add_object('cube', position=(5, 5, -5), scale=(1, 2, 1))

        # for x in range(self.object_handler.max_objects):
        #     for y in range(self.object_handler.max_objects):
        #         for z in range(self.object_handler.max_objects):
        #             self.object_handler.add_object('cube', position=(x * 4, y * 4, z * 4))
        

    def update(self):
        """
        Updates dynamic objects, uniforms, and camera
        """
        self.object_handler.write_instance_data()
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