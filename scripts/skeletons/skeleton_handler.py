import glm
from scripts.collections.collection import Collection
from scripts.skeletons.joints import Joint

class SkeletonHandler():
    def __init__(self, scene, skeletons:list=None):
        self.scene = scene
        self.skeletons = skeletons if skeletons else [] # contains root bones
        
    def update(self, delta_time:float):
        for bone in self.skeletons: bone.update(delta_time)
        
    def add_skeleton(self, collection:Collection, bones=None):
        bone = Bone(self, collection, bones)
        self.skeletons.append(bone)
        return bone
        
    def create_skeleton(self, collection:Collection, bones=None):
        return Bone(self, collection, bones)
    
    def create_joint(self, joint_type:str, parent_offset:glm.vec3, child_offset:glm.vec3, spring_constant:float=1e5, min_radius:float=0, max_radius:float=1):
        
        match joint_type:
            case 'joint' : return Joint(parent_offset, child_offset, spring_constant, min_radius, max_radius)

class Bone():
    def __init__(self, skeleton_handler, collection:Collection, bones=None) -> None:
        self.skeleton_handler = skeleton_handler
        self.collection       = collection
        self.bones            = bones if bones else {} # skeleton, joint
        
    def restrict_bones(self, delta_time:float) -> None:
        for bone, joint in self.bones.items():
            joint.restrict(self.collection, bone.collection, delta_time)
            
    def update(self, delta_time:float):
        self.restrict_bones(delta_time)
        for bone in self.bones: bone.update(delta_time)