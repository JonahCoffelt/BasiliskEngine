import glm
from scripts.collisions.narrow_collisions import get_narrow_collision
from scripts.collisions.broad_collisions import get_broad_collision
from scripts.collection import Collection, Single
from scripts.generic.data_types import vec3

# handles updating collections
class CollectionHandler():
    
    def __init__(self, scene, collections:list[Collection|Single] = None, death_plane:float=-100) -> None:
        self.scene = scene
        if collections: self.collections = collections
        else: self.collections = [] #TODO think of better data structure to prevent duplicates
        self.death_plane = death_plane
        self.collision_depth = 1
        self.time = 1/60
        
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
                    for collider2 in collection2.get_colliders(): 
                        if collider1.static and collider2.static: continue # if neither collider can be moved
                        # broad collision detection
                        if not get_broad_collision(collider1, collider2): continue
                        # narrow collision detection
                        normal, distance, contact_points = get_narrow_collision(collider1.vertices, collider2.vertices, collider1.position, collider2.position)
                        if distance == 0: continue # continue if no collision
                        # immediately resolve penetration
                        if collider1.static: 
                            collection2.position += normal * distance
                        else:
                            if collider2.static: 
                                collection1.position += normal * -distance
                            else:
                                collection1.position += normal * -0.5 * distance
                                collection2.position += normal * 0.5 * distance
                        #for both physics bodies
                        if not (collection1.physics_body or collection2.physics_body): continue
                        self.scene.project.physics_handler.calculate_collisions(normal, collider1, collider2, collection1.physics_body, collection2.physics_body, contact_points, collection1.get_inverse_inertia(), collection2.get_inverse_inertia(), collection1.position, collection2.position)
    
    # create and add to top level collections                    
    def add_collection(self, position:list=None, scale:list=None, rotation:list=None, collections:list=None, physics_body=None, name:str=''):
        self.collections.append(Collection(self, position, scale, rotation, collections=collections, physics_body=physics_body, name=name))
        self.collections[-1].init_physics_body()
        return self.collections[-1]
    def add_single(self, position:glm.vec3|list = None, scale:glm.vec3|list = None, rotation:glm.vec3|list = None, object = None, physics_body = None, collider = None, name:str=''):
        self.collections.append(Single(self, position=position, scale=scale, rotation=rotation, object=object, physics_body=physics_body, collider=collider, name=name))
        self.collections[-1].init_physics_body()
        return self.collections[-1]
    
    # just create
    def create_collection(self, position:list=None, scale:list=None, rotation:list=None, collections:list=None, physics_body=None, name:str=''):
        return Collection(self, position, scale, rotation, collections=collections, physics_body=physics_body, name=name)
    def create_single(self, position:glm.vec3|list = None, scale:glm.vec3|list = None, rotation:glm.vec3|list = None, object = None, physics_body = None, collider = None, name:str=''): 
        return Single(self, position=position, scale=scale, rotation=rotation, object=object, physics_body=physics_body, collider=collider, name=name)