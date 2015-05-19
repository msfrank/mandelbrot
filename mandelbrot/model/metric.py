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
