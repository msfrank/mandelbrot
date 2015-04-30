import pprint

class StructuredMixin(object):
    """
    """
    def destructure(self):
        raise NotImplementedError()
    def __str__(self):
        return pprint.pformat(self.destructure(), indent=4)
    def __repr__(self):
        return str(self)

class SealedException(Exception):
    """
    """
    def __init__(self, obj, field):
        self.obj = obj
        self.field = field
    def __str__(self):
        return "failed to set field '{}': object is sealed".format(self.field)
    def __repr__(self):
        return str(self)

class SealableMixin(object):
    """
    """
    def seal(self):
        self.__setattr__ = self.__sealed

    def __sealed(self, key, value):
        raise SealedException(self, key)
