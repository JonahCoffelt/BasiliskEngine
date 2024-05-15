import numpy as np
import glm


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

        if max_objects > 8000:
            raise ValueError(f"PrefabHandler.add_prefab: Attempted to make a prefab with {max_objects} maximum objects. This number may not exceed 8000 by default.")

        self.prefabs[name] = Prefab(self.project, max_objects, vao, texture_id)


class Prefab:
    def __init__(self, project, max_objects: int=100, vao: str='cube', texture_id: tuple=(2, 1)) -> None:
        # Store the project
        self.project = project
        self.max_objects = max_objects
        self.texture_id = glm.vec2(*texture_id)

        # Store buffer and vao for writing and rendering
        self.vao_name = vao
        self.vao = self.project.vao_handler.vaos[vao]
        self.instance_buffer = self.project.vao_handler.instance_buffers[vao]

        # Dictionary to store instance data
        self.instance_data = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(self.max_objects)], dtype='f4')

        # Vertex data for physics
        vbo = self.project.vao_handler.vbo_handler.vbos[self.project.vao_handler.vao_to_vbo_key[vao]]
        self.triangles = vbo.triangles
        self.unique_points = vbo.unique_points

    def write(self) -> None:
        """
        Writes instance data for a prefab to the buffer of the vao
        """

        self.instance_buffer.write(self.instance_data)
        self.vao.program['textureID'].write(self.texture_id)

    def render(self) -> None:
        """
        Renders instances of the prefabs vao
        """
        self.write()
        self.vao.render(instances=self.max_objects)
