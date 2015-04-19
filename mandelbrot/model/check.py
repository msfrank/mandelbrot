import datetime
import cifparser

from mandelbrot.model import StructuredMixin

class Check(StructuredMixin):
    """
    """
    def __init__(self):
        self.check_id = None
        self.behavior_type = None
        self.policy = {}
        self.properties = {}
        self.metadata = {}

    def get_check_id(self):
        return self.check_id

    def set_check_id(self, check_id):
        assert isinstance(check_id, cifparser.Path)
        self.check_id = check_id

    def get_behavior_type(self):
        return self.behavior_type

    def set_behavior_type(self, behavior_type):
        assert isinstance(behavior_type, str)
        self.behavior_type = behavior_type

    def get_join_timeout(self):
        return self.policy['joinTimeout']

    def set_join_timeout(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['joinTimeout'] = timeout.total_seconds()

    def get_probe_timeout(self):
        return self.policy['probeTimeout']

    def set_probe_timeout(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['probeTimeout'] = timeout.total_seconds()

    def get_alert_timeout(self):
        return self.policy['alertTimeout']

    def set_alert_timeout(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['alertTimeout'] = timeout.total_seconds()

    def get_retirement_age(self):
        return self.policy['leavingTimeout']

    def set_retirement_age(self, timeout):
        assert isinstance(timeout, datetime.timedelta)
        self.policy['leavingTimeout'] = timeout.total_seconds()

    def get_property(self, property_name):
        return self.properties[property_name]

    def list_properties(self):
        return self.properties.items()

    def set_property(self, property_name, property_value):
        assert isinstance(property_name, str)
        assert isinstance(property_value, str)
        self.properties[property_name] = property_value

    def delete_property(self, property_name):
        del self.properties[property_name]

    def flush_properties(self):
        self.properties = {}

    def get_meta_value(self, meta_name):
        return self.metadata[meta_name]

    def list_metadata(self):
        return self.metadata.items()

    def set_meta_value(self, meta_name, meta_value):
        assert isinstance(meta_name, str)
        assert isinstance(meta_value, str)
        self.metadata[meta_name] = meta_value

    def delete_meta_value(self, meta_name):
        del self.metadata[meta_name]

    def flush_metadata(self):
        self.metadata = {}

    def destructure(self):
        structure = {}
        structure['probeType'] = self.behavior_type
        structure['policy'] =  self.policy
        structure['properties'] = self.properties
        structure['metadata'] = self.metadata
        return structure