from scripts.scene import Scene


class ProjectHandler:
    """
    Stores, loads, and saves projects
    """
    def __init__(self, engine, load: str='empty') -> None:
        """
        Initializes the specified projects
        """
        # Stores the engine
        self.engine = engine
        # Creates blank projects dictionary
        self.projects = {}

        # Loads specified projects
        match load:
            case 'empty':
                # Creates a blank project and saves it
                self.projects['Project'] = BlankProject(self.engine)
                self.current_project = self.projects['Project']
            case _:
                # Will load project save
                self.load_project(load)

    def update(self):
        self.current_project.update()

    def render(self):
        self.current_project.render()

    def add_project(self, name: str='Project') -> None:
        """
        Adds a blank project
        """

        # Checks for duplicate names
        project_key, count = name, 1
        while project_key in self.projects:
            project_key = f'{name} ({count})'
            count += 1

        # Adds project
        self.projects[project_key] = BlankProject(self.engine)

    def set_current_project(self, project_key: str='Project') -> None:
        """
        Sets the current project for rendering and editing
        """

        if project_key not in self.projects:
            raise KeyError('ProjectHandler.set_current_project: Given project name does not exist')

        self.current_project = self.projects[project_key]

    def load_project(self, path) -> None:
        """
        Loads a project from a file
        """
        raise RuntimeError('ProjectHandler.load_project: Support for project loading is not yet supported. Can only create blank projects')

    def release(self):
        [project.release() for project in self.projects.values()]

class Project:
    """
    Stores, loads, and saves scene data
    """
    def __init__(self, engine) -> None:
        # Stores the engine
        self.engine = engine
        # Creates blank scenes dictionary
        self.scenes = {}

    def update(self):
        self.current_scene.update()

    def render(self):
        self.current_scene.render()

    def release(self):
        """
        Releases all scenes in project
        """
        [scene.release() for scene in self.scenes.values()]

class BlankProject(Project):
    def __init__(self, engine) -> None:
        super().__init__(engine)
        
        # Adds a blank scene
        self.scenes['Scene'] = Scene(self.engine)
        # Set scene to be rendered and updated
        self.current_scene = self.scenes['Scene']