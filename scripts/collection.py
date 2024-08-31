import glm
from math import sin, cos
from scripts.generic.data_types import vec3

# collection that can contain multiple of each object
class Collection():
    
    def __init__(self, collection_handler, position:glm.vec3|list = None, scale:glm.vec3|list = None, rotation:glm.vec3|list = None, collections:list = None, physics_body=None, name:str = '') -> None:
        self.collection_handler = collection_handler
        # child collections
        self.collections:list[Collection|Single] = collections if collections else []
        self.name = name
        # sets data to sync with objects and containers
        self.position = glm.vec3(position) if position else glm.vec3(0, 0, 0)
        self.scale = glm.vec3(scale) if scale else glm.vec3(1, 1, 1)
        self.rotation = glm.vec3(rotation) if rotation else glm.vec3(0, 0, 0)
        self.sync_data()
        # for physics
        self.physics_body = physics_body
        self.inverse_inertia = self.define_inverse_inertia()
    
    # initialization
    def init_physics_body(self):
        self.remove_physics_bodies()
        if self.physics_body: self.physics_body.rotation = glm.quat(self.rotation)
        
    def remove_physics_bodies(self) -> None:
        for collection in self.collections: collection.remove_physics_bodies()
    
    # updating
    def update(self, delta_time:float) -> None:
        # update physics body
        if self.physics_body:
            self.position += self.physics_body.get_delta_position(delta_time)
            self.rotation = self.physics_body.get_new_rotation(delta_time)
            self.sync_data() 
            
    def sync_data(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None) -> None:
        if self.position.y < self.collection_handler.death_plane: 
            self.position = glm.vec3(5, 5, 5)
            if self.physics_body: 
                self.physics_body.velocity = glm.vec3(0, 0, 0)
                self.physics_body.rotational_velocity = 0
                
        if position or scale or rotation: ... # TODO: add collection recursion
        else: 
            m_mat = get_model_matrix(self.position, self.scale, self.rotation)
            for collection in self.collections: 
                new_position = glm.mul(m_mat, (*collection.position, 1))
                collection.sync_data([*new_position][:3], self.scale, self.rotation)
    
    # getter methods 
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
    
    def add_collection(self, collection): self.collections.append(collection)
    
    # physics function
    def define_inverse_inertia(self) -> glm.mat3x3:
        inertia_data = [(collection.get_inverse_inertia(), collection.position) for collection in self.collections]
        inverse_inertia = glm.mat3x3(0.0)
        # sum child inertia tensors
        for inertia in inertia_data:
            child_inertia = inertia[0]
            child_displacement = inertia[1]
            if not child_inertia: continue # moves on if inertia tensor does not exist
            child_inertia = glm.inverse(child_inertia)
            inverse_inertia += child_inertia + (glm.dot(child_displacement, child_displacement) * glm.mat3x3() - glm.outerProduct(child_displacement, child_displacement))
        return glm.inverse(inverse_inertia) #TODO add parallel axis theorm for mesh center
    
    def get_inverse_inertia(self):
        rot_mat = get_rotation_matrix(self.rotation)
        return rot_mat * self.inverse_inertia * glm.transpose(rot_mat) * (1/self.physics_body.mass if self.physics_body else 1)
        
# collection with optional single model, physic_body, collider
class Single():
    
    def __init__(self, collection_handler, position:glm.vec3|list = None, scale:glm.vec3|list = None, rotation:glm.vec3|list = None, object = None, physics_body = None, collider = None, name='') -> None:
        # sets info
        self.collection_handler = collection_handler
        self.object = object
        self.physics_body = physics_body
        self.collider = collider
        self.name = name
        # sets data to sync with objects and containers
        self.position = glm.vec3(position) if position else glm.vec3(0, 0, 0)
        self.scale = glm.vec3(scale) if scale else glm.vec3(1, 1, 1)
        self.rotation = glm.vec3(rotation) if rotation else glm.vec3(0, 0, 0)
        self.sync_data()
        # for physics
        self.inverse_inertia = self.define_inverse_inertia()
        
    # initialization
    def init_physics_body(self):
        if self.physics_body: self.physics_body.rotation = glm.quat(self.rotation)
            
    def remove_physics_bodies(self):
        self.physics_body = None
    
    # updating
    def sync_data(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None) -> None: #TODO add static syncing
        if self.position.y < self.collection_handler.death_plane: 
            self.position = glm.vec3(0, 10, 0)
            if self.physics_body: 
                self.physics_body.velocity = glm.vec3(0, 0, 0)
                self.physics_body.rotational_velocity = 0
        if position or scale or rotation:
            if self.object: 
                self.object.position = vec3(position)
                self.object.scale = vec3(self.scale * scale)
                self.object.rotation = vec3(rotation + self.rotation)
            if self.collider: 
                self.collider.position = position
                self.collider.scale = self.scale * scale
                self.collider.rotation = rotation + self.rotation
                self.collider.update_geometry()
        else:
            if self.object: 
                self.object.position = vec3(self.position)
                self.object.scale = vec3(self.scale)
                self.object.rotation = vec3(self.rotation)
            if self.collider: 
                self.collider.position = self.position
                self.collider.scale = self.scale
                self.collider.rotation = self.rotation
                self.collider.update_geometry()
            
    def update(self, delta_time:float) -> None:
        # update physics body
        if self.physics_body:
            self.position += self.physics_body.get_delta_position(delta_time)
            self.rotation = self.physics_body.get_new_rotation(delta_time)
            self.sync_data()
            if self.collider:
                self.collider.update_geometry()
        
    # getter methods
    def get_colliders(self) -> list:
        return [self.collider] if self.collider else []
    
    def get_objects(self) -> list:
        return [self.object] if self.object else []
    
    def get_objects_with_path(self) -> tuple[list, list]:
        if self.object: return [self.name], [self.object]
        else: return [], []
        
    def define_inverse_inertia(self) -> glm.mat3x3:
        """returns the inverse inertia tensor of the collider and physics body"""
        if not self.collider: return
        inertia_tensor = glm.mat3x3(0.0)
        for p in self.collider.vbo.unique_points: 
            inertia_tensor[0][0] += p[1] * p[1] + p[2] * p[2]
            inertia_tensor[1][1] += p[0] * p[0] + p[2] * p[2]
            inertia_tensor[2][2] += p[0] * p[0] + p[1] * p[1]
            inertia_tensor[0][1] -= p[0] * p[1]
            inertia_tensor[0][2] -= p[0] * p[2]
            inertia_tensor[1][2] -= p[1] * p[2]
        inertia_tensor[1][0] = inertia_tensor[0][1]
        inertia_tensor[2][0] = inertia_tensor[0][2]
        inertia_tensor[2][1] = inertia_tensor[1][2]
        
        #TODO add parallel axis theorm for geometric center relative to origin
        return glm.inverse(inertia_tensor / len(self.collider.vbo.unique_points))
    
    def get_inverse_inertia(self):
        rot_mat = get_rotation_matrix(self.rotation)
        return rot_mat * self.inverse_inertia * glm.transpose(rot_mat) * (1/self.physics_body.mass if self.physics_body else 1)

# matrix math
def get_model_matrix(position, scale, rotation) -> glm.mat4x4:
    """gets projection matrix from object data"""
    # create blank matrix
    model_matrix = glm.mat4x4()
    # translate, rotate, and scale
    model_matrix = glm.translate(model_matrix, position) # translation
    model_matrix = glm.rotate(model_matrix, rotation.x, glm.vec3(-1, 0, 0)) # x rotation
    model_matrix = glm.rotate(model_matrix, rotation.y, glm.vec3(0, -1, 0)) # y rotation
    model_matrix = glm.rotate(model_matrix, rotation.z, glm.vec3(0, 0, -1)) # z rotation
    model_matrix = glm.scale(model_matrix, scale) # scale
    return model_matrix

def get_rotation_matrix(rotation) -> glm.mat3x3:
    return glm.mat3x3(
        cos(rotation[2]) * cos(rotation[1]), cos(rotation[2]) * sin(rotation[1]) * sin(rotation[0]) - sin(rotation[2]) * cos(rotation[0]), cos(rotation[2]) * sin(rotation[1]) * cos(rotation[0]) + sin(rotation[2]) * sin(rotation[0]),
        sin(rotation[2]) * cos(rotation[1]), sin(rotation[2]) * sin(rotation[1]) * sin(rotation[0]) + cos(rotation[2]) * cos(rotation[0]), sin(rotation[2]) * sin(rotation[1]) * cos(rotation[0]) - cos(rotation[2]) * sin(rotation[0]),
        -sin(rotation[1])            , cos(rotation[1]) * sin(rotation[0])                                       , cos(rotation[1]) * cos(rotation[0])                                       ,
    )
