import numpy as np


class PrefabHandler:
    def __init__(self, project) -> None:
        # Store the project
        self.project = project
        self.prefabs = {}

    def add_prefab(self, name: str='cube', max_objects: int=100, vao: int='cube') -> None:
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

        self.prefabs[name] = Prefab(self.project, max_objects, vao)


class Prefab:
    def __init__(self, project, max_objects: int=100, vao: int='cube') -> None:
        # Store the project
        self.project = project
        self.max_objects = max_objects

        # Store buffer and vao for writing and rendering
        self.vao_name = vao
        self.vao = self.project.vao_handler.vaos[vao]
        self.instance_buffer = self.project.vao_handler.instance_buffers[vao]

        # Dictionary to store instance data
        self.instance_data = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(self.max_objects)], dtype='f4')

    def write(self) -> None:
        """
        Writes instance data for a prefab to the buffer of the vao
        """

        self.instance_buffer.write(self.instance_data)

    def render(self) -> None:
        """
        Renders instances of the prefabs vao
        """
        self.write()
        self.vao.render(instances=self.max_objects)
