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

        self.max_objects = 20  # Cubed for the maximum amount of objects per type
        # Objects list
        self.objects = []
        # Get instance buffers from VAO handler in the scene
        self.instance_buffers = self.scene.vao_handler.instance_buffers
        # Dictionary to store instance data
        self.object_instance_data = {object_type : np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0] for i in range(self.max_objects ** 3)], dtype='f4') for object_type in self.scene.vao_handler.vaos}
        # Availible indices per object type. Used for writting to buffer
        self.object_instance_indices = {object_type : [i for i in range(0, self.max_objects ** 3)] for object_type in self.scene.vao_handler.vaos}

    def render(self):
        for vao in self.scene.vao_handler.vaos:
            self.scene.vao_handler.vaos[vao].render(instances=self.object_instance_data[vao].shape[0])

    def write_instance_data(self) -> None:
        """
        Writes instnace data to vao buffer
        """

        for object_type in self.object_instance_data:
            self.instance_buffers[object_type].write(self.object_instance_data[object_type])

    def add_object(self, type, position: tuple=(0, 0, 0), scale: tuple=(1, 1, 1), rotation: tuple=(0, 0, 0)) -> None:
        """
        Adds an object to the scene
        Must have a type, may be given a position, scale or rotation
        """

        if not len(self.object_instance_indices[type]):
            raise IndexError(f"ObjectHandler.add_object: Object type '{type}' is full. The limit is currently set to {self.max_objects ** 3} objects per type")

        # Gets the first availible object index
        index = self.object_instance_indices[type].pop(0)
        # Adds a new object of the object to the objects list (IDK how else to phrase that lmao)
        self.objects.append(Object(type, index, position, scale, rotation))
        # Updates object's data in the instance data array
        self.object_instance_data[type][index] = [*position, *scale, *rotation]

    def remove_object(self, object) -> None:
        """
        Removes the given object from the scene
        """

        if not object in self.objects:
            raise ValueError(f"ObjectHandler.remove_object: The object given ({object}) was not found in handler's object list")

        # Gets relevant look up data for the object
        type = object.type
        index = object.index

        # Frees up the index for future objects to use
        self.object_instance_indices[type].append(object.index)
        # Sets the instance data to empty
        self.object_instance_data[type][index] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
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
        self.object_instance_data[object.type][object.index] = object.data


class Object:
    def __init__(self, type: str, index: int, position: tuple=(0, 0, 0), scale: tuple=(1, 1, 1), rotation: tuple=(0, 0, 0)) -> None:
        """
        Stores instance data for an object in object.data
        Variables:
            type: str
                Type of object, typically the VAO
            index: int
                Index of the object in the instance data array
            data: [*position=(x, y, z), *scale=(x, y, z), *rotation=(x, y, z)]
                Default value = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        """

        # Variables to access object's data
        self.index = index
        self.type = type
        self.data = [*position, *scale, *rotation]