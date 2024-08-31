import glm

class SkeletonHandler():
    
    def __init__(self, scene, skeletons:list):
        self.scene = scene
        self.skeletons = skeletons

class Bone():
    
    def __init__(self, skeleton_handler:SkeletonHandler, collection) -> None:
        self.skeleton_handler = skeleton_handler
        self.collection = collection
        self.bones = {} # skeleton, joint
        
    def restrict_bones(self) -> None:
        for bone, joint in self.bones.items():
            ...
                
# child free to move and rotate within radius
class Joint(): 
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e4, min_radius:float=0, max_radius:float=1) -> None: 
        # offsets from collection position
        self.parent_offset = parent_offset
        self.child_offset = child_offset
        # spring 
        self.spring_constant = spring_constant
        self.min_radius = min_radius # the minimum radius the child collection can be from its offset
        self.max_radius = max_radius
        
    def restrict(self) -> None:
        ...
        
# child free to move within radius, child must point at offset
class BallJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e4, min_radius:float=0, max_radius:float=1) -> None:
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)
    
# child is locked in place but can rotate on given axis TODO change params
class RotatorJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e4, min_radius:float=0, max_radius:float=1) -> None:
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)
        
# child free to move within radius but can only rotate on given axis TODO change params
class HingeJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e4, min_radius:float=0, max_radius:float=1) -> None:
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)

# child cannot move or be rotated ex pistons
class LockedJoint(Joint):
    def __init__(self, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e4, min_radius:float=0, max_radius:float=1) -> None:
        super().__init__(parent_offset, child_offset, spring_constant, min_radius, max_radius)