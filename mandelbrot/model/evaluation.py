import datetime

from mandelbrot.model import StructuredMixin, SealableMixin

HEALTHY  = 'healthy'
DEGRADED = 'degraded'
FAILED   = 'failed'
UNKNOWN  = 'unknown'

class Evaluation(StructuredMixin, SealableMixin):
    """
    """
    def __init__(self, summary=None, health=None, metrics=None, timestamp=None):
        self.summary = summary
        self.health = health
        self.metrics = metrics
        self.timestamp = timestamp
        self.seal()

    def destructure(self):
        structure = {}
        if self.timestamp is not None:
            structure['timestamp'] = self.timestamp
        if self.summary is not None:
            structure['summary'] = self.summary
        if self.health is not None:
            structure['health'] = self.health
        return structure
