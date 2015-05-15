import datetime

from mandelbrot.model import StructuredMixin, add_constructor

class Duration(StructuredMixin):
    """
    """
    def __init__(self):
        self.timedelta = None

    def get_timedelta(self):
        return self.timedelta

    def set_timedelta(self, value):
        assert isinstance(value, datetime.timedelta)
        self.timedelta = value

    def destructure(self):
        return int(self.timedelta / datetime.timedelta(milliseconds=1))

def _construct_duration(structure):
    assert isinstance(structure, int)
    return datetime.timedelta(milliseconds=structure)

add_constructor(Duration, _construct_duration)
