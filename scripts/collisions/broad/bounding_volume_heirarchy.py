from scripts.collisions.broad.aabb import AABB

class BoundingVolumeHeirarchy():
    def __init__(self, collider_handler):
        self.collider_handler = collider_handler
        self.root             = None
        self.build_tree()
    
    def build_tree(self) -> bool:
        """
        Creates the BVH using info from the colliders
        Returns:
            bool: if the creation of the BVH was successful or not
        """
        # check if there are at least two colliders
        colliders = self.collider_handler.colliders
        if len(colliders) < 2: return False
        
        # define the root AABB (will move down the tree later)
        self.root = AABB(colliders[0], colliders[1], None)
        
        # construct the BVH increamentally
        for collider in colliders[2:]: self.add_collider(collider)
            
    def add_collider(self, collider):
        """
        Adds a collider to the tree and updates accordingly
        """
        # find the best sibling
        c_best, sibling = self.root.find_sibling(collider, 1e10, 0)
        
        # create new parent
        old_parent = sibling.parent
        new_parent = AABB(sibling, collider, old_parent)
        
        if sibling.parent: # if sibling was not the root
            if old_parent.a == sibling: old_parent.a = new_parent
            else:                       old_parent.b = new_parent
            
        else: # if sibling was the root
            # replace root
            self.root = new_parent
            
        # update sibling
        sibling.parent = new_parent
        
        # walk back up tree and refit
        aabb = new_parent
        while aabb: 
            aabb.update_points()
            aabb.update_surface_area()
            
            # rotate tree for minimum surface area
            self.rotate(aabb)
            
            aabb = aabb.parent
        
    def remove_collider(self, collider):
        ...
        
    def rotate(self, aabb):
        ...
        
    def get_collided(self, collider) -> list:
        return self.root.get_collided(collider)