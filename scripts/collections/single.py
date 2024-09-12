import glm
from scripts.generic.math_functions import get_model_matrix, get_rotation_matrix
from scripts.generic.data_types import vec3
from scripts.collections.super_collection import SuperCollection
from scripts.collisions.collider import Collider
from scripts.physics.physics_body_handler import PhysicsBody


# collection with optional single model, physic_body, collider
class Single(SuperCollection):
    def __init__(self, collection_handler, position:glm.vec3|list=None, scale:glm.vec3|list=None, rotation:glm.vec3|list=None, object=None, physics_body=None, collider=None, name=''):
        super().__init__(collection_handler, position, scale, rotation, name)
        # children
        self.object       = object
        self.physics_body = physics_body
        self.collider     = collider
        
        # align children with parent
        #if self.physics_body: 
        self.sync_data()
        
        # for physics
        self.model_matrix    = get_model_matrix(self.position, self.scale, self.rotation)
        self.aligned_inertia = self.define_inverse_inertia()
        if self.collider: self.inverse_inertia = self.get_inverse_inertia()
        
    # initialization
    def init_physics_body(self):
        """
        sets physics body rotation quaternion to current rotation
        """
        if self.physics_body: self.physics_body.rotation = glm.quat(self.rotation)
            
    def remove_physics_bodies(self):
        """
        Removes its physics body, this line is in a function to add recursive support to collections
        """
        self.physics_body = None
    
    # updating
    def sync_data(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None) -> None:
        """
        Syncronizes position, scale, and rotation between the object and collider. Data may be inherited from the parent collection. 
        """
        # death plane, remove if needed
        if self.position.y < self.collection_handler.death_plane: 
            # death plane reaction
            self.position = glm.vec3(0, 10, 0)
            if self.physics_body: 
                self.physics_body.velocity            = glm.vec3(0, 0, 0)
                self.physics_body.rotational_velocity = 0
                
        # syncing with parents and children
        if position or scale or rotation: # if parent
            
            child = glm.quat(self.rotation)
            parent = glm.quat(rotation)
            quat = child * parent
            rotation = glm.eulerAngles(quat)
            
            if self.object: 
                self.object.position = vec3(position)
                self.object.scale    = vec3(self.scale * scale)
                self.object.rotation = vec3(rotation)
                
            if self.collider: 
                self.collider.position = position
                self.collider.scale    = self.scale * scale
                self.collider.rotation = rotation

        else: # if no parent
            if self.object: 
                self.object.position = vec3(self.position)
                self.object.scale    = vec3(self.scale)
                self.object.rotation = vec3(self.rotation)
                
            if self.collider: 
                self.collider.position = self.position
                self.collider.scale    = self.scale
                self.collider.rotation = self.rotation
                
        # update collider data if necessary
        if self.collider:   
            if self.update_scale or self.update_rotation:                         
                self.collider.update_dimensions()
                
            if self.update_position: 
                self.collider.update_geometric_center()
                
            self.collider.update_aabb()
            self.collider.collider_handler.to_update.add(self.collider)

    def update(self, delta_time:float):
        """
        Updates itself by physics body data and syncronizes children. 
        """
        # checks for significant changes
        super().update()
        
        # update physics body
        if self.physics_body:
            self.position += self.physics_body.get_delta_position(delta_time)
            self.physics_body.rotation = glm.quat(self.rotation) # TODO watch this line, it may cause gimble lock
            self.rotation  = self.physics_body.get_new_rotation(delta_time)
            
        
        # make changes to children
        self.sync_data()
        
        # reset update values
        super().after_update()
        
    # getter methods
    def get_colliders(self) -> list:
        """
        Returns collider as a list to be appended during collection. 
        """
        return [self.collider] if self.collider else []
    
    def get_objects(self) -> list:
        """
        Returns object as a list to be appended during collection. 
        """
        return [self.object] if self.object else []
    
    def get_objects_with_path(self) -> tuple[list, list]:
        """
        Returns its object and its name to collection. 
        """
        if self.object: return [self.name], [self.object]
        else: return [], []
        
    def define_inverse_inertia(self) -> glm.mat3x3:
        """
        Returns the inverse inertia tensor of the collider and physics body
        """
        if not self.collider: return
        inertia_tensor = glm.mat3x3(0.0)
        
        for p in self.collider.unique_points: 
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
        return glm.inverse(inertia_tensor / len(self.collider.unique_points))
    
    def get_inverse_inertia(self):
        """
        Returns the inverse inertia tensor with the proper scaling and rotations
        """
        # gets the new inverse inertia if rotation has been changed. 
        if self.update_inertia: 
            rotation_matrix      = get_rotation_matrix(self.rotation) 
            self.inverse_inertia = rotation_matrix * self.aligned_inertia * glm.transpose(rotation_matrix) * (1/self.physics_body.mass if self.physics_body else 1)
            self.update_inertia  = False
            
        # return transformed inertia tensor
        return self.inverse_inertia
    
    def update_parents(self, parent=None):
        """
        Updates the parent collection to its children. If no parameter, set as self.
        """
        if self.collider:
            if parent: self.collider.collection = parent
            else:      self.collider.collection = self
    
    @property
    def collider(self): return self._collider
    
    @collider.setter
    def collider(self, value):
        if isinstance(value, Collider): value.collection = self
        self._collider = value