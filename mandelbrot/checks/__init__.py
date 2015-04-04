
class Check(object):
    """
    """
    def execute(self):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.execute()