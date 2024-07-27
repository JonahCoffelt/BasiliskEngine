from glm import vec3
from scripts.narrow_collisions import get_narrow_collision
from scripts.broad_collisions import get_broad_collision

# handles updating collections
class CollectionHandler():
    
    def __init__(self, scene, collections:list = None, death_plane:float=-100) -> None:
        self.scene = scene
        if collections: self.collections = collections
        else: self.collections = []
        self.death_plane = death_plane
        
    def update(self, delta_time:float):
        # update physics bodies
        for collection in self.collections: collection.update(delta_time)
        # update collisions
        self.resolve_collisions()
        
    def resolve_collisions(self) -> None:
        """runs gjk/epa collision detection and resolution"""
        for i, collection1 in enumerate(self.collections): # gets first collection
            colliders1 = collection1.get_colliders()
            for collection2 in self.collections[i + 1:]: # gets to compare collection
                for collider1 in colliders1: 
                    position1 = vec3(collider1.data[:3]) # preconverts position vector
                    for collider2 in collection2.get_colliders(): 
                        if collider1.static and collider2.static: continue # if neither collider can be moved
                        # broad collision detection
                        if not get_broad_collision(collider1, collider2): continue
                        # narrow collision detection
                        normal, distance, contact_point = get_narrow_collision(collider1.vertices, collider2.vertices, position1, collider2.data[:3]) 
                        if distance == 0: continue # continue if no collision
                        # resolves collision
                        if collider1.static:
                            if not collider2.static: collection2.move(normal * distance)
                        else:
                            if collider2.static: collection1.move(normal * -distance)
                            else:
                                collection1.move(normal * -0.5 * distance)
                                collection2.move(normal * 0.5 * distance)
                        # for both physics bodies
                        if not (collection1.physics_body or collection2.physics_body): continue
                        #print(collection1.physics_body, collection2.physics_body)
                        self.scene.project.physics_handler.calculate_collision(
                            normal, 
                            collider1, 
                            collider2, 
                            collection1.physics_body, 
                            collection2.physics_body, 
                            contact_point)
    
    # create and return                        
    def add_collection(self, position:list=None, scale:list=None, rotation:list=None, collections:list=None, physics_body=None, name:str=''):
        self.collections.append(Collection(self, position, scale, rotation, collections=collections, physics_body=physics_body, name=name))
        return self.collections[-1]
    def add_single(self, position:vec3|list = None, scale:vec3|list = None, rotation:vec3|list = None, object = None, physics_body = None, collider = None, name:str=''):
        self.collections.append(Single(self, position=position, scale=scale, rotation=rotation, object=object, physics_body=physics_body, collider=collider, name=name))
        return self.collections[-1]
    # just create
    def create_collection(self, position:list=None, scale:list=None, rotation:list=None, collections:list=None, physics_body=None, name:str=''):
        return Collection(self, position, scale, rotation, collections=collections, physics_body=physics_body, name=name)
    def create_single(self, position:vec3|list = None, scale:vec3|list = None, rotation:vec3|list = None, object = None, physics_body = None, collider = None, name:str=''): 
        return Single(self, position=position, scale=scale, rotation=rotation, object=object, physics_body=physics_body, collider=collider, name=name)
        
# collection that can contain multiple of each object
class Collection():
    
    def __init__(self, collection_handler:CollectionHandler, position:vec3|list = None, scale:vec3|list = None, rotation:vec3|list = None, collections:list = None, physics_body=None, name:str = '') -> None:
        self.collection_handler = collection_handler
        self.collections:list[Collection|Single] = collections if collections else []
        self.physics_body = physics_body
        self.name = name
        # sets data to sync with objects and containers
        position = position if position else [0, 0, 0]
        scale = scale if scale else [1, 1, 1]
        rotation = rotation if rotation else [0, 0, 0]
        self.data = [*position] + [*scale] + [*rotation]
        self.sync_data()
        
    def remove_physics_bodies(self):
        for collection in self.collections: collection.remove_physics_bodies()
    
    def update(self, delta_time:float) -> None:
        # update physics body
        if self.physics_body:
            self.move(self.physics_body.get_delta_position(delta_time))
            self.set_data(self.data[:6] + [*self.physics_body.get_new_rotation(self.data[6:], delta_time)])
            self.sync_data()
        
    def get_colliders(self):
        colliders = []
        for collection in self.collections: colliders += collection.get_colliders()
        return colliders
    
    def get_objects(self):
        objects = []
        for collection in self.collections: objects += collection.get_objects()
        return objects
    
    def get_objects_with_path(self):
        names = []
        objects = []
        for collection in self.collections: 
            name, object = collection.get_objects_with_path()
            names += name
            objects += object
        return [f'{self.name}>{name}' for name in names], objects
    
    def move(self, delta_position) -> None:
        for collection in self.collections: collection.move(delta_position)
        
    def add_collection(self, collection):
        self.collections.append(collection)
        
    def sync_data(self):
        if self.data[1] < self.collection_handler.death_plane: self.data[:3] = [0, 0, 0]
        for collection in self.collections: collection.sync_data(self.data)
        
    def set_data(self, data:list) -> None:
        self.data = data
        self.sync_data()
        
    def get_name_tree(self) -> str:
        name = f'{self.name}({'p' if self.physics_body else ''})['
        for collection in self.collections: name += f'{collection.get_name_tree()}, '
        return name [:-2] + ']'
        
# collection with optional single model, physic_body, collider
class Single():
    
    def __init__(self, collection_handler:CollectionHandler, position:vec3|list = None, scale:vec3|list = None, rotation:vec3|list = None, object = None, physics_body = None, collider = None, name='') -> None:
        # sets info
        self.collection_handler = collection_handler
        self.object = object
        self.physics_body = physics_body
        self.collider = collider
        self.name = name
        # sets data to sync with objects and containers
        position = position if position else [0, 0, 0]
        scale = scale if scale else [1, 1, 1]
        rotation = rotation if rotation else [0, 0, 0]
        self.data = [*position] + [*scale] + [*rotation]
        self.sync_data()
        
    def update(self, delta_time:float) -> None:
        # update physics body
        if self.physics_body:
            self.move(self.physics_body.get_delta_position(delta_time))
            self.set_data(self.data[:6] + [*self.physics_body.get_new_rotation(self.data[6:], delta_time)])
            
    def remove_physics_bodies(self):
        self.physics_body = None
            
    def set_data(self, data:list) -> None:
        self.data = data
        self.sync_data()
        
    def sync_data(self, data:list=None) -> None:
        if data:
            if self.object: self.collection_handler.scene.object_handler.set_object_data(self.object, multiply(data[3:6], add(self.data[:3], data[:3])), multiply(self.data[3:6], data[3:6]), add(self.data[6:], data[6:]))
            if self.collider: self.collider.set_data(multiply(data[3:6], add(self.data[:3], data[:3])) + multiply(self.data[3:6], data[3:6]) + add(self.data[6:], data[6:]))
        else:
            if self.object: self.collection_handler.scene.object_handler.set_object_data(self.object, self.data[:3], self.data[3:6], self.data[6:])
            if self.collider: self.collider.set_data(self.data)
        
    def set_position(self, position:vec3|list) -> None:
        self.data = [*position] + self.data[3:9]
        
    def get_colliders(self):
        return [self.collider] if self.collider else []
    
    def get_objects(self):
        return [self.object] if self.object else []
    
    def get_objects_with_path(self):
        if self.object: return [self.name], [self.object]
        else: return [], []
    
    def move(self, delta_position) -> None:
        self.set_position(self.data[:3] + delta_position)
        
    def get_name_tree(self) -> str:
        return f'{self.name}({'o' if self.object else ''}{'p' if self.physics_body else ''}{'c' if self.collider else ''})'
        
def add(list1, list2) -> list:
    # adds individual entries of lists of equal length
    assert len(list1) == len(list2), 'lists are not equal length'
    return [list1[i] + list2[i] for i in range(len(list1))]

def multiply(list1, list2) -> list:
    # adds individual entries of lists of equal length
    assert len(list1) == len(list2), 'lists are not equal length'
    return [list1[i] * list2[i] for i in range(len(list1))]