import decimal

from mandelbrot.model import StructuredMixin, add_constructor, construct
from mandelbrot.model.timestamp import Timestamp

class CheckMetrics(StructuredMixin):
    """
    """
    def __init__(self):
        self.timestamp = None
        self.metrics = {}

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        assert isinstance(timestamp, Timestamp)
        self.timestamp = timestamp

    def get_metric(self, metric_name):
        return self.metrics[metric_name]

    def list_metrics(self):
        return self.metrics.items()

    def set_metric(self, metric_name, metric):
        assert isinstance(metric_name, str)
        assert isinstance(metric, float)
        self.metrics[metric_name] = metric

    def delete_metric(self, metric_name):
        del self.metrics[metric_name]

    def flush_metrics(self):
        self.metrics = {}

    def destructure(self):
        structure = {}
        structure['timestamp'] = self.timestamp.destructure()
        structure['metrics'] = self.metrics
        return structure

class CheckMetricsPage(StructuredMixin):
    """
    """
    def __init__(self):
        self.check_metrics = []
        self.last = None
        self.exhausted = None

    def append_check_metrics(self, check_metrics):
        assert isinstance(check_metrics, CheckMetrics)
        return self.check_metrics.append(check_metrics)

    def list_check_metrics(self):
        return self.check_metrics

    def get_last(self):
        return self.last

    def set_last(self, last):
        assert isinstance(last, str)
        self.last = last

    def get_exhausted(self):
        return self.exhausted

    def set_exhausted(self, exhausted):
        assert isinstance(exhausted, bool)
        self.exhausted = exhausted

    def destructure(self):
        structure = {}
        return structure

def _construct_check_metrics(structure):
    check_metrics = CheckMetrics()
    timestamp = construct(Timestamp, structure['timestamp'])
    check_metrics.set_timestamp(timestamp)
    for name,value in structure['metrics'].items():
        check_metrics.set_metric(name, float(value))
    return check_metrics

add_constructor(CheckMetrics, _construct_check_metrics)

def _construct_check_metrics_page(structure):
    page = CheckMetricsPage()
    for value in structure['history']:
        check_metrics = construct(CheckMetrics, value)
        page.append_check_metrics(check_metrics)
    if 'last' in structure:
        page.set_last(structure['last'])
    if 'exhausted' in structure:
        page.set_exhausted(structure['exhausted'])
    return page

add_constructor(CheckMetricsPage, _construct_check_metrics_page)
