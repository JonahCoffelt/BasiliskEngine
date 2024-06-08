import numpy as np
import array
from numba import njit
import glm

@njit
def distance(a, b):
    return np.sqrt(np.sum((a - b) ** 2))

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

        # Temporal Threads
        self.threads = 4
        self.current_thread = 0
        self.cumulative_data = {prefab : array.array('f') for prefab in self.prefabs} 

        # Objects list
        self.objects = []
        self.chunks = {}
        self.chunk_size = 50
        self.render_distance = 225
        self.in_range_chunks = []
        
    def render(self):
        for prefab in self.prefabs.values():
            prefab.render()

    def add_object(self, prefab, position: tuple=(0, 0, 0), scale: tuple=(1, 1, 1), rotation: tuple=(0, 0, 0)) -> None:
        """
        Adds an object to the scene
        Must have a prefab, may be given a position, scale or rotation
        """

        chunk_pos = int(position[0] // self.chunk_size), int(position[1] // self.chunk_size), int(position[2] // self.chunk_size)

        chunk_key = f'{chunk_pos[0]},{chunk_pos[1]},{chunk_pos[2]}'
        if not chunk_key in self.chunks: self.chunks[chunk_key] = [glm.vec3((chunk_pos[0] + .5) * self.chunk_size, (chunk_pos[1] + .5) * self.chunk_size, (chunk_pos[2] + .5) * self.chunk_size)]
        
        # Adds a new object of the object to the objects list (IDK how else to phrase that lmao)
        self.objects.append(Object(prefab, position, scale, rotation))
        self.chunks[chunk_key].append(self.objects[-1])

    def remove_object(self, object) -> None:
        """
        Removes the given object from the scene
        """

        if not object in self.objects:
            raise ValueError(f"ObjectHandler.remove_object: The object given ({object}) was not found in handler's object list")


        self.objects.remove(object)


    def get_chunks_in_range(self):
        chunk_keys = []

        cam_pos = self.scene.camera.position
        cam_chunk_pos = (int(cam_pos.x // self.chunk_size), int(cam_pos.y // self.chunk_size), int(cam_pos.z // self.chunk_size))
        render_range = int(self.render_distance // self.chunk_size)

        for x in range(cam_chunk_pos[0] - render_range, cam_chunk_pos[0] + render_range + 1):
            for y in range(cam_chunk_pos[1] - render_range, cam_chunk_pos[1] + render_range + 1):
                for z in range(cam_chunk_pos[2] - render_range, cam_chunk_pos[2] + render_range + 1):
                    chunk_key = f'{x},{y},{z}'
                    if not chunk_key in self.chunks: continue
                    chunk_objects = self.chunks[chunk_key]

                    dist = glm.length(chunk_objects[0] - cam_pos)
                    if dist > self.render_distance: continue

                    chunk_keys.append(chunk_key)
        
        return chunk_keys

    def get_objects_in_range(self):
        objects = []

        for chunk in self.in_range_chunks:
            chunk_objects = self.chunks[chunk]
            objects.extend(chunk_objects)
        
        return objects

    def update(self):
        thread_data = {prefab : [] for prefab in self.prefabs}

        removes = []


        # Loop through all chunks in range
        for chunk in self.in_range_chunks:
            # Get the objects from the chunk
            objects = self.chunks[chunk]
            # Loop through the objects, skipping the objects not on the current thread
            for object in objects[self.current_thread+1:len(objects):self.threads]:
                # Add the objects data to the current thread data
                data = object.data
                thread_data[object.prefab].append(data)
            
                # Dont update static objects
                if 'static' in object.tags: continue

                # Get the chunk the object is in
                new_chunk = int(data[0] // self.chunk_size), int(data[1] // self.chunk_size), int(data[2] // self.chunk_size)
                new_chunk_position = glm.vec3((new_chunk[0] + .5) * self.chunk_size, (new_chunk[1] + .5) * self.chunk_size, (new_chunk[2] + .5) * self.chunk_size)

                # Dont update object chunk if it is in same chunk as before
                if new_chunk_position == objects[0]: continue

                # Get the chunk key of the object's new chunk
                new_chunk_key = f'{new_chunk[0]},{new_chunk[1]},{new_chunk[2]}'

                # Create new chunk if needed
                if not new_chunk_key in self.chunks: 
                    self.chunks[new_chunk_key] = [new_chunk_position]

                # Move the object
                self.chunks[new_chunk_key].append(object)
                removes.append((chunk, object))
                #self.chunks[chunk].remove(object)

                # Update the in range chunks
                self.in_range_chunks.append(new_chunk_key)

        for object in removes:
            self.chunks[object[0]].remove(object[1])

        for prefab in self.prefabs:
            data = []
            for sublist in thread_data[prefab]:
                data.extend(sublist)

            self.cumulative_data[prefab].extend(array.array('f', data))

        self.current_thread += 1
        if self.current_thread == self.threads:
            for prefab in self.cumulative_data:
                self.prefabs[prefab].write(self.cumulative_data[prefab])
                self.cumulative_data[prefab] = array.array('f')
            self.current_thread = 0
            self.in_range_chunks = self.get_chunks_in_range()


class Object:
    def __init__(self, prefab: str, position: tuple=(0, 0, 0), scale: tuple=(1, 1, 1), rotation: tuple=(0, 0, 0)) -> None:
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
        self.prefab = prefab
        self.data = [*position, *scale, *rotation]

        self.tags = set([])
        self.components = set([])
    
    def __repr__(self) -> str:
        return f'<Object: {self.prefab} {self.data[:3]}>'