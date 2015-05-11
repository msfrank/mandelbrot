import datetime

from mandelbrot.model import StructuredMixin
from mandelbrot.model.constants import CheckHealth, health_types

HEALTHY = CheckHealth.HEALTHY
DEGRADED = CheckHealth.DEGRADED
FAILED = CheckHealth.FAILED
UNKNOWN = CheckHealth.UNKNOWN

class Evaluation(StructuredMixin):
    """
    """
    def __init__(self):
        self.summary = None
        self.health = None
        self.metrics = {}
        self.timestamp = None

    def get_summary(self):
        return self.summary

    def set_summary(self, summary):
        assert isinstance(summary, str)
        self.summary = summary

    def get_health(self):
        return self.health

    def set_health(self, health):
        assert health in health_types
        self.health = health

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        assert isinstance(timestamp, datetime.datetime)
        self.timestamp = timestamp

    def get_metric(self, metric_name):
        return self.metrics[metric_name]

    def list_metrics(self):
        return self.metrics.items()

    def set_metric(self, metric_name, metric_value):
        assert isinstance(metric_name, str)
        assert isinstance(metric_value, int) or isinstance(metric_value, float)
        self.metrics[metric_name] = metric_value

    def delete_metric(self, metric_name):
        del self.metrics[metric_name]

    def flush_metrics(self):
        self.metrics = {}

    def destructure(self):
        structure = {}
        if self.timestamp is not None:
            structure['timestamp'] = self.timestamp
        if self.summary is not None:
            structure['summary'] = self.summary
        if self.health is not None:
            structure['health'] = self.health
        if len(self.metrics) > 0:
            structure['metrics'] = self.metrics
        return structure
