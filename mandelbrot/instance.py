import os
import logging

log = logging.getLogger("mandelbrot.instance")

class Instance(object):
    """
    """
    def __init__(self, path, id, checks):
        """
        """
        self.path = os.path.abspath(path)
        self.id = id
        self.checks = checks

    def exists(self):
        pass

    def rename(self, instance_id):
        pass

    def delete(self):
        pass

def open_instance(path, mode, **flags):
    """
    :return:
    """
    flag_creat = bool(flags.get('create', False))
    flag_excl = bool(flags.get('exclusive', False))
    checks = []
    return None
