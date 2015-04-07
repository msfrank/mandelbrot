
class Check(object):
    """
    """
    def configure(self, ns):
        pass

    def execute(self):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.execute()
