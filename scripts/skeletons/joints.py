import glm
from math import sqrt, acos, sin, cos
from scripts.collections.collection import Collection

# child free to move and rotate within radius
class Joint(): 
    def __init__(self, child_bone, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e10, min_radius:float=0, max_radius:float=1): # parent and child not saved for splitting
        # child bone
        self.child_bone = child_bone
        # offsets from collection position
        self.parent_offset          = glm.vec3(parent_offset)
        self.original_parent_offset = glm.vec3(self.parent_offset.x, self.parent_offset.y, self.parent_offset.z)
        self.child_offset_mag       = glm.length(child_offset) # radial joint
        # spring 
        self.spring_constant = spring_constant
        self.min_radius      = min_radius # the minimum radius the child collection can be from its offset
        self.max_radius      = max_radius
        
    def restrict(self, parent:Collection, child:Collection, delta_time:float):
        """
        Restricts the child to the parent using rk4
        """
        origin       = parent.position + self.parent_offset
        displacement = child.position - origin
        
        if glm.length(displacement) < 1e-7: return # no movement needed
        direction    = glm.normalize(displacement)
        
        # if the collection has a physics body do this TODO fix rk4 for springs
        if child.physics_body:
            
            # acceleration = self.get_spring_acceleration(child, direction, origin)
            # velocity     = child.physics_body.velocity
            # position     = child.position
            
            # k1_pos, k1_vel = delta_time * velocity,                  delta_time * acceleration(position)
            # k2_pos, k2_vel = delta_time * (velocity + 0.5 * k1_vel), delta_time * acceleration(position + 0.5 * k1_pos)
            # k3_pos, k3_vel = delta_time * (velocity + 0.5 * k2_vel), delta_time * acceleration(position + 0.5 * k2_pos)
            # k4_pos, k4_vel = delta_time * (velocity + k3_vel),       delta_time * acceleration(position + k3_pos)
            
            # child.position              += (k1_pos + 2 * k2_pos + 2 * k3_pos + k4_pos) / 6
            # child.physics_body.velocity += (k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel) / 6
            
            # print((k1_vel + 2 * k2_vel + 2 * k3_vel + k4_vel) / 6)
            
            force_spring = -self.spring_constant * direction * (glm.length(origin - child.position) - self.child_offset_mag)
            force_dampen = -2 * sqrt(self.spring_constant + child.physics_body.mass) * child.physics_body.velocity
            force_total = (force_spring + force_dampen) * (0.5 if child.physics_body and parent.physics_body else 1)
            
            if child.physics_body:
                acceleration = force_total / child.physics_body.mass
                child.physics_body.velocity += acceleration * delta_time
                child.position += child.physics_body.velocity * delta_time
            if parent.physics_body:
                acceleration = -force_total / parent.physics_body.mass
                parent.physics_body.velocity += acceleration * delta_time
                parent.position += parent.physics_body.velocity * delta_time
            
        # snap to position if it does not
        else: 
            child.position = origin + direction * self.child_offset_mag
    
    def get_spring_acceleration(self, constant_child:Collection, direction:glm.vec3, origin:glm.vec3):
        """
        Creates an acceleration function for spring joints
        """
        def acceleration(position:glm.vec3) -> glm.vec3:
            return -self.spring_constant * direction * (glm.length(origin - position) - self.child_offset_mag) / constant_child.physics_body.mass
        return acceleration
    
    def rotate_parent_offset(self, rotation:glm.vec3):
        """
        Rotate the original parent offset point by the given rotation
        """
        rotated_quat = glm.inverse(rotation) * glm.quat(0, *self.original_parent_offset) * rotation
        self.parent_offset = glm.vec3(rotated_quat.x, rotated_quat.y, rotated_quat.z) #+ self.original_parent_offset
        
# child free to move within radius, child must point at offset
class BallJoint(Joint):
    def __init__(self, child_bone, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius)
        self.original_child_offset = glm.quat(0, *child_offset)
        self.original_child_rotation = glm.inverse(glm.quat(self.child_bone.collection.rotation))
        
    def restrict(self, parent:Collection, child:Collection, delta_time:float):
        super().restrict(parent, child, delta_time)
        # set child's rotation to face parent
        # origin = parent.position + self.parent_offset
        current_offset = parent.position - child.position # TODO update child facing 
        
        if glm.length(current_offset) < 1e-6: return # if there is no offset from the origin, do nothing
        
        # gets the difference quaternion to get point quaterion from axis angle
        current_forward = self.original_child_rotation * -self.original_parent_offset
        current_offset = glm.normalize(current_offset)
        
        # calculates the axis angle to turn into quaternion
        axis = glm.cross(current_forward, current_offset)
        angle = glm.acos(glm.dot(glm.normalize(current_forward), current_offset))
        
        if glm.length(axis) < 1e-6: axis = glm.vec3(0, 1, 0)
        
        # get new quaternion rotation
        rot = glm.inverse(glm.angleAxis(angle, glm.normalize(axis))) * self.original_child_rotation
        
        self.child_bone.collection.rotation = glm.eulerAngles(rot)
    
# child is locked in place but can rotate on given axis TODO change params
class RotatorJoint(Joint):
    def __init__(self, child_bone, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius)
        
# child free to move within radius but can only rotate on given axis TODO change params
class HingeJoint(Joint):
    def __init__(self, child_bone, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius)

# child cannot move or be rotated. ex pistons
class PistonJoint(Joint):
    def __init__(self, child_bone, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e2, min_radius:float=0, max_radius:float=1):
        super().__init__(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius)