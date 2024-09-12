import glm
from scripts.collections.collection import Collection
from scripts.skeletons.joints import *

class SkeletonHandler():
    def __init__(self, scene, skeletons:list=None):
        self.scene     = scene
        self.skeletons = skeletons if skeletons else [] # contains root bones
        
    def update(self, delta_time:float):
        """
        Updates all the skeletons on the top level/root list
        """
        for bone in self.skeletons: bone.update(delta_time)
        
    def add_skeleton(self, collection:Collection, joints=None):
        """
        Creates a skeleton and adds it to the top level list. 
        """
        bone = Bone(self, collection, joints)
        self.skeletons.append(bone)
        return bone
        
    def create_skeleton(self, collection:Collection, joints=None):
        """
        Creates the skeleton and returns it but does not add it to the top level list. 
        """
        return Bone(self, collection, joints)
    
    def create_joint(self, joint_type:str, child_bone, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e3, min_radius:float=0, max_radius:float=1):
        """
        Creates a joint based on the given string. 
        """
        match joint_type:
            case 'free'      : return       Joint(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius)
            case 'ball'      : return   BallJoint(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius)
            case 'piston'    : return PistonJoint(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius) # TODO make operational
            case 'rotator'   : return       Joint(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius) # TODO make operational
            case 'hinge'     : return       Joint(child_bone, parent_offset, child_offset, spring_constant, min_radius, max_radius) # TODO make operational

class Bone():
    def __init__(self, skeleton_handler, collection:Collection, joints=None) -> None:
        self.skeleton_handler  = skeleton_handler
        self.collection        = collection
        self.original_inv_quat = glm.inverse(glm.quat(self.collection.rotation))
        self.joints            = joints if joints else [] # skeleton, joint
        
    def restrict_bones(self, delta_time:float) -> None:
        """
        Restricts the chlid bones based on their respective joints. Also adds spring forces
        """
        # gets difference in rotations and applies to joints
        rotation = glm.quat(self.collection.rotation) * self.original_inv_quat
        for joint in self.joints: joint.rotate_parent_offset(rotation)
            
        # apply restrictions
        for joint in self.joints: joint.restrict(self.collection, joint.child_bone.collection, delta_time)
            
    def update(self, delta_time:float):
        """
        Restricts bones and restricts children from joints
        """
        self.restrict_bones(delta_time)
        for joint in self.joints: joint.child_bone.update(delta_time)