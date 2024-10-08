import glm
import numpy as np
from scripts.collisions.collider import Collider
from scripts.collisions.broad.bounding_volume_heirarchy import BoundingVolumeHeirarchy
from scripts.collisions.narrow.narrow_collisions import get_narrow_collision
from scripts.physics.impulse import calculate_collisions
from scripts.transform_handler import TransformHandler

class ColliderHandler():
    """controls import and interaction between colliders"""
    def __init__(self, scene) -> None:
        """stores imports and bodies"""
        self.scene = scene
        # vbos dictionary
        self.vbos = self.scene.vao_handler.vbo_handler.vbos
        self.colliders = []
        # transforms
        self.transform_handler = TransformHandler(self.scene)
        self.to_update = set([])
        
    def add(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None, vbo:str='cube', static = True, elasticity:float=0.1, kinetic_friction:float=0.4, static_friction:float=0.8):
        """adds new collider with corresponding object"""
        self.colliders.append(Collider(self, position, scale, rotation, vbo, static, elasticity, kinetic_friction, static_friction))
        return self.colliders[-1]
    
    def resolve_collisions(self):
        # get broad collisions
        self.bvh.build_tree() # TODO replace with better update system
        
        needs_narrow = {}
        for collider in self.colliders:
            broad_collisions = self.bvh.get_collided(collider)
            if len(broad_collisions) < 1: continue
            needs_narrow[collider] = set(broad_collisions)
        
        # updates vertcies
        self.to_update.intersection_update(needs_narrow.keys())
        self.update_vertices_transform()
        
        already_collided = {collider : set([]) for collider in self.colliders}
            
        # narrow collisions
        for collider1, possible_colliders in needs_narrow.items():
            for collider2 in possible_colliders:
                # check if already collided
                if collider2 in already_collided[collider1] or collider1 in already_collided[collider2]: continue
                
                normal, distance, contact_points = get_narrow_collision(collider1.vertices, collider2.vertices, collider1.position, collider2.position)
                if distance == 0: continue # continue if no collision
                # log collision
                already_collided[collider1].add(collider2)
                already_collided[collider2].add(collider1)
                
                # immediately resolve penetration
                collection1 = collider1.collection
                collection2 = collider2.collection
                
                if collider1.static: 
                    collection2.position += normal * distance
                else:
                    if collider2.static: 
                        collection1.position += normal * -distance
                    else:
                        collection1.position += normal * 0.5 * -distance
                        collection2.position += normal * 0.5 * distance
                #for both physics bodies
                if not (collection1.physics_body or collection2.physics_body): continue
                calculate_collisions(normal, collider1, collider2, collection1.physics_body, collection2.physics_body, contact_points, collection1.get_inverse_inertia(), collection2.get_inverse_inertia(), collection1.position, collection2.position)
    
    def get_model_matrix(self, data:list) -> glm.mat4:
        """gets projection matrix from object data"""
        # create blank matrix
        model_matrix = glm.mat4()
        # translate, rotate, and scale
        model_matrix = glm.translate(model_matrix, data[:3]) # translation
        model_matrix = glm.rotate(model_matrix, data[6], glm.vec3(-1, 0, 0)) # x rotation
        model_matrix = glm.rotate(model_matrix, data[7], glm.vec3(0, -1, 0)) # y rotation
        model_matrix = glm.rotate(model_matrix, data[8], glm.vec3(0, 0, -1)) # z rotation
        model_matrix = glm.scale(model_matrix, data[3:6]) # scale
        return model_matrix
    
    def get_real_vertex_locations(self, vbo) -> list:
        """gets the in-world locations of the collider vertices"""
        model_matrix = self.get_model_matrix()
        return [glm.vec3((new := glm.mul(model_matrix, (*vertex, 1)))[0], new[1], new[2]) for vertex in self.vbos[vbo].unique_points]

    def construct_bvh(self):
        self.bvh = BoundingVolumeHeirarchy(self)
    
        
    def update_vertices_transform(self):
        """
        Updates all necessary vertices using the transform handler
        """
            
        batch_data = []
        vert_rows = []
        
        for collider in self.to_update:
            # stack vertcies with center and dimensions
            vertex_data = np.copy(collider.unique_points)
            rows = vertex_data.shape[0]
            
            # adds transformation to point
            model_data = np.array([*collider.position, *collider.rotation, *collider.scale])
            collider_data = np.zeros(shape=(rows, 12), dtype="f4")
            
            collider_data[:,:3] = vertex_data
            collider_data[:,3:] = model_data
            
            batch_data.append(collider_data)
            vert_rows.append(rows)
        
        # Combine all meshes into a single array
        if len(batch_data) < 1:
            self.to_update = set([])
            return
            
        batch_data = np.vstack(batch_data, dtype="f4")
        data = self.transform_handler.transform('model_transform', batch_data)
        
        for collider, count in zip(self.to_update, vert_rows):
            # get vertices
            vertices = []
            for _ in range(count):
                vertices.append(glm.vec3(data[:3]))
                data = data[3:]
            collider.vertices = vertices
            
        self.to_update = set([])