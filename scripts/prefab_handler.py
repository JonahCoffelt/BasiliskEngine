import glm
import array
import moderngl as mgl

class PrefabHandler:
    def __init__(self, project) -> None:
        # Store the project
        self.project = project
        self.prefabs = {}

    def add_prefab(self, name: str='cube', max_objects: int=100, vao: int='cube', texture_id: tuple=(2, 1)) -> None:
        """
        Creates a prefab which can be used for objects.
        Args:
            name: str
                The name that the prefab will be accessed by
            max_objects: int
                The maximum number of objects of this prefab. This number may not exceed 8000 by default
            vao: int
                The name of the vao to be used for this prefab
        """

        # if max_objects > self.project.vao_handler.max_objects ** 3:
        #     raise ValueError(f"PrefabHandler.add_prefab: Attempted to make a prefab with {max_objects} maximum objects. This number may not exceed 8000 by default.")

        self.prefabs[name] = Prefab(self.project, max_objects, name, texture_id)


class Prefab:
    def __init__(self, project, max_objects: int=100, vao: str='cube', texture_id: tuple=(4, 0)) -> None:
        # Store the project
        self.project = project
        self.max_objects = max_objects
        self.texture_id = glm.vec2(*texture_id)

        # Store buffer and vao for writing and rendering
        self.vao_name = vao
        self.vao = self.project.vao_handler.vaos[vao]
        self.instance_buffer = self.project.vao_handler.instance_buffers[vao]

        # Dictionary to store instance data
        self.instance_data = array.array('f')

        # Vertex data for physics
        vbo = self.project.vao_handler.vbo_handler.vbos[self.project.vao_handler.vao_to_vbo_key[vao]]
        self.unique_points = vbo.unique_points

    def write(self, data) -> None:
        """
        Writes instance data for a prefab to the buffer of the vao
        """

        self.instance_data = data
        self.instance_buffer.clear()
        self.instance_buffer.write(self.instance_data)

    def render(self) -> None:
        """
        Renders instances of the prefabs vao
        """

        self.vao.program['textureID'].write(self.texture_id)
        self.vao.render(instances=len(self.instance_data))


class Softbody(Prefab):
    def __init__(self, project, max_objects: int = 100, texture_id: tuple = (3, 0), vbo=None) -> None:
        # Store the project
        self.project = project
        self.max_objects = max_objects
        self.texture_id = glm.vec2(*texture_id)

        # Vao data
        self.program = self.project.vao_handler.shader_handler.programs['g_buffer']
        self.vbo = vbo

        # Store buffer and vao for writing and rendering
        self.vao_name = 'softbody'
        self.instance_buffer = self.project.ctx.buffer(reserve=(5 ** 3) * (9 * 4), dynamic=True)
        self.vao = self.project.ctx.vertex_array(self.program, [(self.vbo.vbo, self.vbo.format, *self.vbo.attribs), 
                                            (self.instance_buffer, '3f 3f 3f /i', *['in_instance_position', 'in_instance_scale', 'in_instance_rotation'])], 
                                            skip_errors=True)

        # Dictionary to store instance data
        self.instance_data = array.array('f')

        # Vertex data for physics
        self.unique_points = self.vbo.unique_points

    def reconstruct_mesh(self):
        self.vbo.reconstruct_mesh()
