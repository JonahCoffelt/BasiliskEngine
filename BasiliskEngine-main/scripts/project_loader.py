import os
import glm
from scripts.scene import Scene

def load_project(project, directory: str):
    with open(f'{directory}/proj.save', 'r') as project_file:
        # Split the file into list of lines
        lines = list(project_file)
        i = 0
        line = lines[0].strip()
        # Find the initial scene indicator
        while line != 'initial scene':
            line = lines[i].strip()
            i += 1

        # Get the initial scene data
        i += 1
        initial_scene = lines[i].strip()
        i += 1

        # Find the prefabs indicator
        while line != 'prefabs':
            line = lines[i].strip()
            i += 1
        
        # Get each prefab's data
        prefabs = []
        while i < len(lines):
            line = lines[i].strip()
            if len(line.split(' ')) == 3: prefabs.append(line.split(' '))
            i += 1


    for prefab in prefabs:
        project.prefab_handler.add_prefab(prefab[0], int(prefab[1]), prefab[2])
    # Loads all the scenes to the project class
    load_scenes(project, f'{directory}/scenes')
    # Selects the initial scene
    project.set_scene(initial_scene)


def load_scenes(project, directory: str) -> None:
    # Loop through each file in directory
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        # Checking if it is a file
        if not os.path.isfile(file): continue
        # Checking if its a scene file
        if not file[-6:] == '.scene': continue
        project.scenes[filename[:-6]] = load_scene(project, file)


def load_scene(project, path: str) -> Scene:
    """
    Loads the camera and objects from a scene file
    """
    with open(path, 'r') as scene_file:
        # Split the file into list of lines
        lines = list(scene_file)
        i = 0
        line = lines[0].strip()

        # Find the camera indicator
        while line != 'camera':
            line = lines[i].strip()
            i += 1
        
        # Get the camera data
        i += 1
        camera_data = [float(point) for point in lines[i].strip().split(' ')]
        i += 1

        # Find the objects indicator
        while line != 'objects':
            line = lines[i].strip()
            i += 1

        # Get each object's data
        objects = []
        while i < len(lines):
            line = lines[i].strip()
            if len(line.split(' ')) == 10: objects.append([line.split(' ')[0]] + [float(point) for point in line.split(' ')[1:]])
            i += 1

    # Create an empty scene
    scene = Scene(project.engine, project)
    # Update the camera's position
    scene.camera.position = glm.vec3(camera_data[:3])
    # Add all objects
    for object in objects:
        scene.object_handler.add_object(object[0], object[1:4], object[4:7], object[7:])
        scene.collider_handler.add_collider(scene.object_handler.objects[-1].data, scene.object_handler.objects[-1].prefab, static = False)
    
    return scene