# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import cifparser

from mandelbrot.model import StructuredMixin
from mandelbrot.model.check import Check
from mandelbrot.model.metric import Metric

class Registration(StructuredMixin):
    """
    """
    def __init__(self):
        self.agent_id = None
        self.agent_type = None
        self.checks = {}
        self.metrics = {}
        self.metadata = {}

    def get_agent_id(self):
        return self.agent_id

    def set_agent_id(self, agent_id):
        assert isinstance(agent_id, cifparser.Path)
        self.agent_id = agent_id

    def get_agent_type(self):
        return self.agent_type

    def set_agent_type(self, agent_type):
        assert isinstance(agent_type, str)
        self.agent_type = agent_type

    def get_check(self, check_id):
        return self.checks[check_id]

    def list_checks(self):
        return self.checks.items()

    def set_check(self, check_id, check):
        assert isinstance(check_id, cifparser.Path)
        assert isinstance(check, Check)
        self.checks[check_id] = check

    def delete_check(self, check_id):
        del self.checks[check_id]

    def flush_checks(self):
        self.checks = {}

    def get_metric(self, check_id, metric_name):
        return self.metrics[(check_id,metric_name)]

    def list_metrics(self):
        return self.metrics.items()

    def set_metric(self, check_id, metric_name, metric):
        assert isinstance(check_id, cifparser.Path)
        assert isinstance(metric_name, str)
        assert isinstance(metric, Metric)
        self.metrics[(check_id,metric_name)] = metric

    def delete_metric(self, check_id, metric_name):
        del self.metrics[(check_id,metric_name)]

    def flush_metrics(self):
        self.metrics = {}

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
        structure['agentId'] = str(self.agent_id)
        structure['agentType'] = self.agent_type
        structure['metadata'] = self.metadata
        checks = {}
        for check_id,check in self.checks.items():
            check_id = str(check_id)
            checks[check_id] = check.destructure()
        structure['checks'] = checks
        metrics = {}
        for (check_id,metric_name),metric in self.metrics.items():
            metric_source = str(check_id) + ':' + metric_name
            metrics[metric_source] = metric.destructure()
        structure['metrics'] = metrics
        return structure
