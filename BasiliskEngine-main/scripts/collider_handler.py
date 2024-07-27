import glm

class ColliderHandler():
    """controls import and interaction between colliders"""
    def __init__(self, scene) -> None:
        """stores imports and bodies"""
        self.scene = scene
        # Prefabs dictionary
        self.prefabs = self.scene.project.prefab_handler.prefabs
        self.colliders = []
        
    def add_collider(self, data:list=None, prefab=None, static = True):
        """adds new collider with corresponding object"""
        self.colliders.append(Collider(self, data, prefab, static))
        return self.colliders[-1]
    
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
    
    def get_real_vertex_locations(self, prefab) -> list:
        """gets the in-world locations of the collider vertices"""
        model_matrix = self.get_model_matrix()
        #return [glm.vec3(model_matrix * vertex) for vertex in self.collider_handler.prefabs[self.prefab].unique_points]
        return [glm.vec3((new := glm.mul(model_matrix, (*vertex, 1)))[0], new[1], new[2]) for vertex in self.prefabs[prefab].unique_points]

class Collider():
    """parent class for collider"""
    def __init__(self, collider_handler:ColliderHandler, data:list, prefab, static = True, elasticity = 0.9) -> None:
        """stores data for collider"""
        self.collider_handler = collider_handler
        # data
        if data: self.data = data # pos [:3], scale [3:6], rot[6:]
        else: self.data = [0, 0, 0, 1, 1, 1, 0, 0, 0]
        self.prefab = prefab
        # geometry
        self.vertices = self.get_real_vertex_locations() # vertices must be created before everything else
        self.geometric_center = self.get_geometric_center()
        # physics
        self.static = static
        self.elasticity = elasticity
        self.inertia_tensor = self.get_inertia_tensor()
        self.dimensions = self.get_dimensions()
        
    def set_data(self, data:list) -> None:
        oldData = self.data[:]
        self.data = data
        # updates vertices from new data
        self.vertices = self.get_real_vertex_locations()
        self.geometric_center = self.get_geometric_center()
        if oldData[3:6] != self.data[3:6]: 
            self.dimensions = self.get_dimensions() # scale changed
            if oldData[6:] != self.data[6:]: self.inertia_tensor = self.get_inertia_tensor() # rotation changed
    
    def set_position(self, position) -> None:
        """sets position of collider, takes glm and list"""
        self.set_data([*position] + self.data[3:])
        
    def set_scale(self, scale) -> None:
        """sets scale of collider, takes glm and list"""
        self.set_data(self.data[:3] + [*scale] + self.data[6:])
        
    def set_rotation(self, rotation) -> None:
        """sets rotation of collider, takes glm and list"""
        self.set_data(self.data[:6] + [*rotation])
        
    def get_model_matrix(self) -> glm.mat4:
        """gets projection matrix from object data"""
        # create blank matrix
        model_matrix = glm.mat4()
        # translate, rotate, and scale
        model_matrix = glm.translate(model_matrix, self.data[:3]) # translation
        model_matrix = glm.rotate(model_matrix, self.data[6], glm.vec3(-1, 0, 0)) # x rotation
        model_matrix = glm.rotate(model_matrix, self.data[7], glm.vec3(0, -1, 0)) # y rotation
        model_matrix = glm.rotate(model_matrix, self.data[8], glm.vec3(0, 0, -1)) # z rotation
        model_matrix = glm.scale(model_matrix, self.data[3:6]) # scale
        return model_matrix
    
    def get_real_vertex_locations(self) -> list:
        """gets the in-world locations of the collider vertices"""
        model_matrix = self.get_model_matrix()
        #return [glm.vec3(model_matrix * vertex) for vertex in self.collider_handler.prefabs[self.prefab].unique_points]
        return [glm.vec3((new := glm.mul(model_matrix, (*vertex, 1)))[0], new[1], new[2]) for vertex in self.collider_handler.prefabs[self.prefab].unique_points]
    
    def get_geometric_center(self) -> glm.vec3: # not being used at the moment
        """returns the center of a convex polytope"""
        minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
        for point in self.vertices:
            for i in range(3):
                if point[i] > maximums[i]: maximums[i] = point[i]
                if point[i] < minimums[i]: minimums[i] = point[i]
        vec = glm.vec3(*[(maximums[i] + minimums[i]) / 2 for i in range(3)])
        return vec
    
    def get_inertia_tensor(self):
        inertia_tensor = glm.mat3(0.0)  # Initialize 3x3 matrix with zeros
        
        for v in self.vertices:
            # Convert glm.vec3 to numpy array for easier math
            r = glm.vec3(v - self.geometric_center)
            r_mag2 = glm.dot(r, r)  # ||r||^2
            
            # Compute the outer product r_outer
            r_outer = glm.mat3(
                r.x * r.x, r.x * r.y, r.x * r.z,
                r.y * r.x, r.y * r.y, r.y * r.z,
                r.z * r.x, r.z * r.y, r.z * r.z
            )
            
            # Contribution to the inertia tensor
            inertia_contribution = (r_mag2 * glm.mat3(1.0) - r_outer)
            inertia_tensor += inertia_contribution
            
        # If mass is not uniform, multiply by mass; for simplicity, assume mass = 1 here
        return inertia_tensor
    
    def get_radius_to_point(self, point:glm.vec3) -> float:
        return point - self.geometric_center
    
    def get_dimensions(self):
        minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
        for point in self.collider_handler.prefabs[self.prefab].unique_points:
            for i in range(3):
                if point[i] * self.data[3 + i] > maximums[i]: maximums[i] = point[i] * self.data[3 + i]
                if point[i] * self.data[3 + i] < minimums[i]: minimums[i] = point[i] * self.data[3 + i]
        dim = glm.vec3(*[(maximums[i] - minimums[i]) for i in range(3)])
        return dim