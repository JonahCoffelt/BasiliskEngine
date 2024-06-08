import numpy as np
from scripts.vbo_handler import VBOHandler
from scripts.shader_handler import ShaderHandler


class VAOHandler:
    """
    Stores VBO and shader handlers. Creates VAOs
    """
    def __init__(self, project):
        self.project = project
        self.ctx = self.project.ctx
    
        self.shader_handler = ShaderHandler(self.project)
        self.vbo_handler = VBOHandler(self.ctx)

        self.vaos = {}
        self.vao_to_vbo_key = {}
        self.instance_buffers = {}
        self.vao_templates = {}
        self.max_objects = 40  # Cubed for the maximum amount of objects per type

        self.add_vao('frame', 'frame', 'frame', instances=False)

    def add_vao(self, name: str='cube', program_key: str='g_buffer', vbo_key: str='cube', instances=True):
        """
        Adds a new VAO with a program and VBO. Creates an empty instance buffer
        """

        # Gets program and vbo
        program = self.shader_handler.programs[program_key]
        vbo = self.vbo_handler.vbos[vbo_key]
        if instances:
            # Creates a vao with program, vbo, and instance buffer
            instance_buffer = self.ctx.buffer(reserve=(self.max_objects ** 3) * (9 * 4), dynamic=True)
            vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs), 
                                                (instance_buffer, '3f 3f 3f /i', *['in_instance_position', 'in_instance_scale', 'in_instance_rotation'])], 
                                                skip_errors=True)


            self.vaos[name], self.instance_buffers[name], self.vao_to_vbo_key[name] = vao, instance_buffer, vbo_key
        else:
            vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
            self.vaos[name], self.vao_to_vbo_key[name] = vao, vbo_key
    
    def add_template(self, name: str, program_key: str='g_buffer', vbo_key: str='cube'):
        """
        Creates a template of a vao to be used by prefabs.
        This allows for less CPU time spent on buffer managment in exchange for more memory overhead.
        """

        self.vao_templates[name] = (program_key, vbo_key)

    def release(self):
        """
        Releases all VAOs and shader programs in handler
        """
        
        self.vbo_handler.release()
        self.shader_handler.release()