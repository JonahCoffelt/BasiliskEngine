import numpy as np
from scripts.vbo_handler import VBOHandler
from scripts.shader_handler import ShaderHandler


class VAOHandler:
    """
    Stores VBO and shader handlers. Creates VAOs
    """
    def __init__(self, scene):
        self.scene = scene
        self.ctx = self.scene.ctx
    
        self.shader_handler = ShaderHandler(self.scene)
        self.vbo_handler = VBOHandler(self.ctx)

        self.vaos = {}
        self.instance_buffers = {}
        self.max_objects = 20  # Cubed for the maximum amount of objects per type

        self.vaos['cube'], self.instance_buffers['cube'] = self.add_vao()

    def add_vao(self, program_key: str='default', vbo_key: str='cube'):
        """
        Adds a new VAO with a program and VBO. Creates an empty instance buffer
        """

        # Gets program and vbo
        program = self.shader_handler.programs[program_key]
        vbo = self.vbo_handler.vbos[vbo_key]
        # Creates a vao with program, vbo, and instance buffer
        instance_buffer = self.ctx.buffer(reserve=(self.max_objects ** 3) * (9 * 4))
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs), 
                                              (instance_buffer, '3f 3f 3f /i', *['in_instance_position', 'in_instance_scale', 'in_instance_rotation'])], 
                                              skip_errors=True)

        return vao, instance_buffer
    
    def release(self):
        """
        Releases all VAOs and shader programs in handler
        """
        
        self.vbo_handler.release()
        self.shader_handler.release()