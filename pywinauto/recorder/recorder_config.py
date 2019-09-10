class RecorderConfig(object):
    def __init__(self):
        self.cmd = None
        self.process = None
        self.verbose = False
        self.out = None
        self.backend = None
        self.key_only = False
        self.scale_click = False

    def apply(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)
