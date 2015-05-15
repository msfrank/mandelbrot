import datetime

from mandelbrot.model import StructuredMixin, add_constructor

UTC = datetime.timezone(datetime.timedelta(0), 'Z')

class Timestamp(StructuredMixin):
    """
    """
    def __init__(self):
        self.datetime = None

    def get_datetime(self):
        return self.datetime

    def set_datetime(self, value):
        assert isinstance(value, datetime.datetime)
        assert value.tzinfo.utcoffset == 0
        self.datetime = value

    def destructure(self):
        return int(self.datetime.timestamp() * 1000.0)

def _construct_timestamp(structure):
    assert isinstance(structure, int)
    timestamp = structure / 1000.0
    return datetime.datetime.fromtimestamp(timestamp, UTC)

add_constructor(Timestamp, _construct_timestamp)
