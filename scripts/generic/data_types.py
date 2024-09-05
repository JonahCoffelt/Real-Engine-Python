class vec3(list):
    def __init__(self, iterable, update_func=None):
        self.update_func = update_func
        super().__init__(item for item in iterable)

    def __setitem__(self, index, item):
        if self.update_func: self.update_func()
        super().__setitem__(index, item)
    
    @property
    def x(self):
        return self[0]
    @property
    def y(self):
        return self[1]
    @property
    def z(self):
        return self[2]
    
    @x.setter
    def x(self, value):
        self[0] = value
    @y.setter
    def y(self, value):
        self[1] = value
    @z.setter
    def z(self, value):
        self[2] = value