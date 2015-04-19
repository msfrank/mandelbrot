import datetime

from mandelbrot.model import StructuredMixin

class Metric(StructuredMixin):
    """
    """
    def __init__(self):
        self.metric_source = None
        self.source_type = None
        self.metric_unit = None
        self.step = None
        self.heartbeat = None
        self.cf = None

    def get_metric_source(self):
        return self.metric_source

    def set_metric_source(self, metric_source):
        assert isinstance(metric_source, str)
        self.metric_source = metric_source

    def get_source_type(self):
        return self.source_type

    def set_source_type(self, source_type):
        assert isinstance(source_type, str)
        self.source_type = source_type

    def get_metric_unit(self):
        return self.metric_unit

    def set_metric_unit(self, metric_unit):
        assert isinstance(metric_unit, str)
        self.metric_unit = metric_unit

    def get_step(self):
        return self.step

    def set_step(self, step):
        assert isinstance(step, datetime.timedelta)
        self.step = step.total_seconds()

    def get_heartbeat(self):
        return self.heartbeat

    def set_heartbeat(self, heartbeat):
        assert isinstance(heartbeat, datetime.timedelta)
        self.heartbeat = heartbeat.total_seconds()

    def get_cf(self):
        return self.cf

    def set_cf(self, cf):
        assert isinstance(cf, str)
        self.cf = cf

    def destructure(self):
        structure = {}
        structure['sourceType'] = self.source_type
        structure['metricUnit'] = self.metric_unit
        if self.step is not None:
            structure['step'] = self.step
        if self.heartbeat is not None:
            structure['heartbeat'] = self.heartbeat
        if self.cf is not None:
            structure['cf'] = self.cf
        return structure
