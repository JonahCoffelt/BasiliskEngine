import glm
from scripts.collections.collection import Collection, Single

# handles updating collections
class CollectionHandler():
    def __init__(self, scene, collections:list[Collection|Single] = None, death_plane:float=-100):
        self.scene       = scene
        self.death_plane = death_plane
        if collections: self.collections = collections
        else: self.collections           = [] #TODO think of better data structure to prevent duplicates
        
    def update(self, delta_time:float):
        """
        Updates all top level collections.
        """
        # update physics bodies
        for collection in self.collections: collection.update(delta_time)
    
    # create and add to top level collections                    
    def add_collection(self, position:list=None, scale:list=None, rotation:list=None, collections:list=None, physics_body=None, name:str=''):
        """
        Adds a collection to the top level array and returns it. 
        """
        collection = Collection(self, position, scale, rotation, collections, physics_body, name)
        collection.init_physics_body()
        collection.update_parents()
        self.collections.append(collection)
        return collection
    
    def add_single(self, position:glm.vec3|list = None, scale:glm.vec3|list = None, rotation:glm.vec3|list = None, object = None, physics_body = None, collider = None, name:str=''):
        """
        Adds a single to the top level array and returns it.
        """
        single = Single(self, position, scale, rotation, object, physics_body, collider, name)
        single.init_physics_body()
        single.update_parents()
        self.collections.append(single)
        return single
    
    # just create
    def create_collection(self, position:list=None, scale:list=None, rotation:list=None, collections:list=None, physics_body=None, name:str=''):
        """
        Only creates a collectino and returns it, does not add to top level array. 
        """
        return Collection(self, position, scale, rotation, collections, physics_body, name)
    
    def create_single(self, position:glm.vec3|list = None, scale:glm.vec3|list = None, rotation:glm.vec3|list = None, object = None, physics_body = None, collider = None, name:str=''): 
        """
        Only creates a single and returns it, does not add to the top level array.
        """
        return Single(self, position, scale, rotation, object, physics_body, collider, name)