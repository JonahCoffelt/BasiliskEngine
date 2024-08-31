import glm

class ColliderHandler():
    """controls import and interaction between colliders"""
    def __init__(self, scene) -> None:
        """stores imports and bodies"""
        self.scene = scene
        # vbos dictionary
        self.vbos = self.scene.vao_handler.vbo_handler.vbos
        self.colliders = []
        
    def add_collider(self, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None, vbo:str='cube', static = True, elasticity:float=0.1, kinetic_friction:float=0.4, static_friction:float=0.8):
        """adds new collider with corresponding object"""
        self.colliders.append(Collider(self, position, scale, rotation, vbo, static, elasticity, kinetic_friction, static_friction))
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
    
    def get_real_vertex_locations(self, vbo) -> list:
        """gets the in-world locations of the collider vertices"""
        model_matrix = self.get_model_matrix()
        return [glm.vec3((new := glm.mul(model_matrix, (*vertex, 1)))[0], new[1], new[2]) for vertex in self.vbos[vbo].unique_points]

class Collider():
    def __init__(self, collider_handler:ColliderHandler, position:glm.vec3=None, scale:glm.vec3=None, rotation:glm.vec3=None, vbo:str='cube', static = True, elasticity:float=0.1, kinetic_friction:float=0.4, static_friction:float=0.8) -> None:

        self.collider_handler = collider_handler
        self.position = glm.vec3(position) if position else glm.vec3(0, 0, 0)
        self.scale = glm.vec3(scale) if scale else glm.vec3(1, 1, 1)
        self.rotation = glm.vec3(rotation) if rotation else glm.vec3(0, 0, 0)
        # mesh
        self.vbo = self.collider_handler.vbos[vbo]
        # geometry
        self.vertices = self.get_real_vertex_locations() # vertices must be created before everything else
        self.dimensions = self.get_dimensions()
        self.geometric_center = self.get_geometric_center()
        # physics
        self.base_volume = 8
        self.static = static
        self.elasticity = elasticity
        
        self.static_friction = kinetic_friction
        self.kinetic_friction = static_friction
        
    def update_geometry(self) -> None: #TODO only call this once per update
        self.vertices = self.get_real_vertex_locations()
        self.geometric_center = self.get_geometric_center()
        self.dimensions = self.get_dimensions()
        
    def get_model_matrix(self) -> glm.mat4:
        """gets projection matrix from object data"""
        # create blank matrix
        model_matrix = glm.mat4()
        # translate, rotate, and scale
        model_matrix = glm.translate(model_matrix, self.position) # translation
        model_matrix = glm.rotate(model_matrix, self.rotation.x, glm.vec3(-1, 0, 0)) # x rotation
        model_matrix = glm.rotate(model_matrix, self.rotation.y, glm.vec3(0, -1, 0)) # y rotation
        model_matrix = glm.rotate(model_matrix, self.rotation.z, glm.vec3(0, 0, -1)) # z rotation
        model_matrix = glm.scale(model_matrix, self.scale) # scale
        return model_matrix
    
    def get_real_vertex_locations(self) -> list:
        """gets the in-world locations of the collider vertices"""
        model_matrix = self.get_model_matrix()
        return [glm.vec3((new := glm.mul(model_matrix, (*[float(f) for f in vertex], 1)))[0], new[1], new[2]) for vertex in self.vbo.unique_points]
    
    def get_geometric_center(self) -> glm.vec3: # not being used at the moment
        """returns the center of a convex polytope"""
        minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
        for point in self.vertices:
            for i in range(3):
                if point[i] > maximums[i]: maximums[i] = point[i]
                if point[i] < minimums[i]: minimums[i] = point[i]
        center = glm.vec3([(maximums[i] + minimums[i])/2 for i in range(3)])
        return center
    
    def get_radius_to_point(self, point:glm.vec3) -> float:
        return point - self.geometric_center
    
    def get_dimensions(self) -> glm.vec3:
        minimums, maximums = [1e10, 1e10, 1e10], [-1e10, -1e10, -1e10]
        for point in self.vbo.unique_points:
            for i in range(3):
                if point[i] * self.scale[i] > maximums[i]: maximums[i] = point[i] * self.scale[i]
                if point[i] * self.scale[i] < minimums[i]: minimums[i] = point[i] * self.scale[i]
        dim = glm.vec3(*[(maximums[i] - minimums[i]) for i in range(3)])
        return dim
    
    def get_volume(self) -> None:
        return self.base_volume * self.scale.x * self.scale.y * self.scale.z
