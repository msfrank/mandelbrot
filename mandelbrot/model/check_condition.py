import datetime

from mandelbrot.model import StructuredMixin, add_constructor, construct
from mandelbrot.model.timestamp import Timestamp
from mandelbrot.model.constants import lifecycle_types, health_types

class CheckCondition(StructuredMixin):
    """
    """
    def __init__(self):
        self.timestamp = None
        self.lifecycle = None
        self.summary = None
        self.health = None
        self.correlation = None
        self.acknowledged = None
        self.squelched = None

    def get_timestamp(self):
        return self.timestamp

    def set_timestamp(self, timestamp):
        assert isinstance(timestamp, Timestamp)
        self.timestamp = timestamp

    def get_lifecycle(self):
        return self.lifecycle

    def set_lifecycle(self, lifecycle):
        assert lifecycle in lifecycle_types
        self.lifecycle = lifecycle

    def get_health(self):
        return self.health

    def set_health(self, health):
        assert health in health_types
        self.health = health

    def get_summary(self):
        return self.summary

    def set_summary(self, summary):
        assert isinstance(summary, str)
        self.summary = summary

    def get_correlation(self):
        return self.correlation

    def set_correlation(self, correlation):
        assert isinstance(correlation, str)
        self.correlation = correlation

    def get_acknowledged(self):
        return self.acknowledged

    def set_acknowledged(self, acknowledged):
        assert isinstance(acknowledged, str)
        self.acknowledged = acknowledged

    def get_squelched(self):
        return self.squelched

    def set_squelched(self, squelched):
        assert isinstance(squelched, bool)
        self.squelched = squelched

    def destructure(self):
        structure = {}
        structure['timestamp'] = self.timestamp.destructure()
        structure['lifecycle'] = self.lifecycle
        structure['health'] = self.health
        structure['squelched'] = self.squelched
        if self.summary is not None:
            structure['summary'] = self.summary
        if self.correlation is not None:
            structure['correlation'] = self.correlation
        if self.acknowledged is not None:
            structure['acknowledged'] = self.acknowledged
        return structure

class CheckConditionPage(StructuredMixin):
    """
    """
    def __init__(self):
        self.check_conditions = []
        self.last = None
        self.exhausted = None

    def append_check_condition(self, check_condition):
        assert isinstance(check_condition, CheckCondition)
        return self.check_conditions.append(check_condition)

    def list_check_conditions(self):
        return self.check_conditions

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

def _construct_check_condition(structure):
    check_condition = CheckCondition()
    timestamp = construct(Timestamp, structure['timestamp'])
    check_condition.set_timestamp(timestamp)
    check_condition.set_lifecycle(structure['lifecycle'])
    check_condition.set_health(structure['health'])
    check_condition.set_squelched(structure['squelched'])
    if 'summary' in structure:
        check_condition.set_summary(structure['summary'])
    if 'correlation' in structure:
        check_condition.set_correlation(structure['correlation'])
    if 'acknowledged' in structure:
        check_condition.set_acknowledged(structure['acknowledged'])
    return check_condition

add_constructor(CheckCondition, _construct_check_condition)

def _construct_check_condition_page(structure):
    page = CheckConditionPage()
    for value in structure['history']:
        check_condition = construct(CheckCondition, value)
        page.append_check_condition(check_condition)
    if 'last' in structure:
        page.set_last(structure['last'])
    if 'exhausted' in structure:
        page.set_exhausted(structure['exhausted'])
    return page

add_constructor(CheckConditionPage, _construct_check_condition_page)
