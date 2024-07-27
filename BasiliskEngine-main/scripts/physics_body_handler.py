import glm
import random

class PhysicsBodyHandler():
    def __init__(self, scene, physics_bodies:list = None) -> None:
        self.scene = scene
        self.physics_bodies = physics_bodies if physics_bodies else []
        
    def add_physics_body(self, mass:float = 1, velocity:glm.vec3 = None, rotational_velocity:int = 0, axis_of_rotation:glm.vec3 = None):
        # add physics body and return
        self.physics_bodies.append(PhysicsBody(mass, velocity, rotational_velocity, axis_of_rotation))
        return self.physics_bodies[-1]

class PhysicsBody():
    def __init__(self, mass:float = 1, velocity:glm.vec3 = None, rotational_velocity:int = 0, axis_of_rotation:glm.vec3 = None) -> None:
        self.mass = mass
        self.velocity = velocity if velocity else glm.vec3(0, 0, 0)
        self.rotational_velocity = rotational_velocity
        self.axis_of_rotation = axis_of_rotation if axis_of_rotation else glm.vec3(1, 0, 0)
        
    def get_delta_position(self, delta_time:float) -> glm.vec3:
        """gets the delta position of the physics body"""
        #if random.randint(1, 1000) == 1: self.velocity[1] = 10
        return self.velocity * delta_time
    
    def get_new_rotation(self, rotation:list, delta_time:float):
        iq = glm.quat(rotation)
        theta = self.rotational_velocity * delta_time
        rq = glm.angleAxis(theta, glm.normalize(self.axis_of_rotation) if glm.length(self.axis_of_rotation) > 0 else glm.vec3(0, 0, 0))
        rq = rq * iq
        return glm.eulerAngles(rq)