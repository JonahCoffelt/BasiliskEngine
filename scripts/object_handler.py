import numpy as np


class ObjectHandler:
    def __init__(self, scene) -> None:
        """
        Sets up instance data arrays and buffers for current VAOs
        Creates empty list of objects
        """

        # Stores the scene
        self.scene = scene
        self.ctx = self.scene.ctx

        # Prefabs dictionary
        self.prefabs = self.scene.project.prefab_handler.prefabs
        # Availible indices per object prefab. Used for writting to buffer
        self.instance_indices = {prefab : [i for i in range(0, self.prefabs[prefab].max_objects)] for prefab in self.prefabs}

        # Objects list
        self.objects = []
        
    def render(self):
        for prefab in self.prefabs.values():
            prefab.render()

    def use(self):
        for prefab in self.prefabs.values():
            prefab.instance_data = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(prefab.max_objects)], dtype='f4')
        for object in self.objects:
            self.prefabs[object.prefab].instance_data[object.index] = object.data

    def add_object(self, prefab, position: tuple=(0, 0, 0), scale: tuple=(1, 1, 1), rotation: tuple=(0, 0, 0)) -> None:
        """
        Adds an object to the scene
        Must have a prefab, may be given a position, scale or rotation
        """

        if not len(self.instance_indices[prefab]):
            raise IndexError(f"ObjectHandler.add_object: Object prefab '{prefab}' is full. The limit is currently set to {self.prefabs[prefab].max_objects} objects per prefab")

        # Gets the first availible object index
        index = self.instance_indices[prefab].pop(0)
        # Adds a new object of the object to the objects list (IDK how else to phrase that lmao)
        self.objects.append(Object(prefab, index, position, scale, rotation))
        # Updates object's data in the instance data array
        self.prefabs[prefab].instance_data[index] = [*position, *scale, *rotation]

    def remove_object(self, object) -> None:
        """
        Removes the given object from the scene
        """

        if not object in self.objects:
            raise ValueError(f"ObjectHandler.remove_object: The object given ({object}) was not found in handler's object list")

        # Gets relevant look up data for the object
        prefab = object.prefab
        index = object.index

        # Frees up the index for future objects to use
        self.instance_indices[prefab].append(object.index)
        # Sets the instance data to empty
        self.prefabs[prefab].instance_data[index] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # Removes object from handler's object list
        self.objects.remove(object)

    def set_object_data(self, object, position=None, scale=None, rotation=None) -> None:
        """
        Sets the position, scale, or rotation of the object.
        If nothing is given for a particular value it will not be changed
        Args:
            position: tuple=(x, y, z)
            scale: tuple=(x, y, z)
            rotation: tuple=(x, y, z)
        """

        # Updates each value if given
        if position: object.data[:3] = position
        if scale: object.data[3:6] = scale
        if rotation: object.data[6:] =  rotation

        # Updates data in instance data array
        self.prefabs[object.prefab].instance_data[object.index] = object.data


class Object:
    def __init__(self, prefab: str, index: int, position: tuple=(0, 0, 0), scale: tuple=(1, 1, 1), rotation: tuple=(0, 0, 0)) -> None:
        """
        Stores instance data for an object in object.data
        Variables:
            prefab: str
                Prefab of object, typically the VAO
            index: int
                Index of the object in the instance data array
            data: [*position=(x, y, z), *scale=(x, y, z), *rotation=(x, y, z)]
                Default value = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        """

        # Variables to access object's data
        self.index = index
        self.prefab = prefab
        self.data = [*position, *scale, *rotation]