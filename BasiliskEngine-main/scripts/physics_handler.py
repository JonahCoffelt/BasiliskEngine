import glm

class PhysicsHandler:
    """controls the movement of physics bodies"""
    def __init__(self, scene = None, accelerations:list = [glm.vec3(0, -4, 0)]) -> None:
        """stores scene and accelerations list in project"""
        self.scene = scene
        self.accelerations = accelerations # constant accelerations in the scene
        
    def update(self, delta_time:float) -> None:
        """moves physics bodies and collections"""
        # update physics bodies 
        if self.scene is None: return # when project has no scene
        physics_body_handler = self.scene.physics_body_handler
        # accelerate all physics bodies by external accelerations
        for body in physics_body_handler.physics_bodies:
            for acceleration in self.accelerations: body.velocity += acceleration * delta_time
        # update collections
        self.scene.collection_handler.update(delta_time)
        
    def add_acceleration(self, acceleration:list) -> None:
        """adds a constant acceleration to project physics engine"""
        self.accelerations.append(acceleration)
        
    def calculate_impulse(self, inv_mass1, inv_mass2, velocity1, velocity2, omega1, omega2, radius1, radius2, inv_inertia1, inv_inertia2, elasticity1, elasticity2, collision_normal) -> glm.vec3:
        relative_velocity = (velocity2 + glm.cross(omega2 * radius2, radius2)) - (velocity1 + glm.cross(omega1 * radius1, radius1))
        relative_normal = glm.dot(relative_velocity, collision_normal)
        if relative_normal > 0:
            return glm.vec3(0, 0, 0)
        
        cross1 = glm.cross(radius1, collision_normal)
        cross2 = glm.cross(radius2, collision_normal)
        
        term1 = inv_mass1 + inv_mass2
        term2 = glm.dot(collision_normal, glm.cross(inv_inertia1 * cross1, radius1)) + glm.dot(collision_normal, glm.cross(inv_inertia2 * cross2, radius2))
        
        # temp line
        if term1 + term2 == 0: return 0
        
        magnitude = -(1 + min(elasticity1, elasticity2)) * relative_normal / (term1 + term2)
        return magnitude * collision_normal
    
    def apply_impulse(self, radius, impulse, inv_inertia, inv_mass, physics_body, contact_point) -> None:
        # Update linear velocity
        physics_body.velocity += impulse * inv_mass
        torque = glm.cross(radius, impulse)
        delta_omega = inv_inertia * torque
        angular_velocity_vector = physics_body.axis_of_rotation * physics_body.rotational_velocity + delta_omega
        physics_body.rotational_velocity = 0 #glm.length(angular_velocity_vector)
        physics_body.axis_of_rotation = glm.normalize(angular_velocity_vector)
        

    def calculate_collision(self, normal: glm.vec3, collider1, collider2, physics_body1, physics_body2, contact_point: glm.vec3) -> None:
        # calculate inverses
        inv_mass1 = 1 / physics_body1.mass if physics_body1 else 0
        inv_mass2 = 1 / physics_body2.mass if physics_body2 else 0
        
        inv_inertia1 = glm.inverse(collider1.get_inertia_tensor()) if physics_body1 else glm.mat3(0.0)
        inv_inertia2 = glm.inverse(collider2.get_inertia_tensor()) if physics_body2 else glm.mat3(0.0)
        
        # calculate radii
        radius1 = collider1.get_radius_to_point(contact_point)
        radius2 = collider2.get_radius_to_point(contact_point)
        
        # adjust variables for static bodies
        velocity1 = physics_body1.velocity if physics_body1 else glm.vec3(0, 0, 0)
        velocity2 = physics_body2.velocity if physics_body2 else glm.vec3(0, 0, 0)
        
        rotational_velocity1 = physics_body1.rotational_velocity if physics_body1 else 0
        rotational_velocity2 = physics_body2.rotational_velocity if physics_body2 else 0
        
        # calculate impulse
        impulse = self.calculate_impulse(inv_mass1, inv_mass2, velocity1, velocity2, rotational_velocity1, rotational_velocity2, radius1, radius2, inv_inertia1, inv_inertia2, collider1.elasticity, collider2.elasticity, normal)
        
        # apply impulse
        if physics_body1:
            self.apply_impulse(radius1, -impulse, inv_inertia1, inv_mass1, physics_body1, contact_point)
        if physics_body2:
            self.apply_impulse(radius2, impulse, inv_inertia2, inv_mass2, physics_body2, contact_point)
