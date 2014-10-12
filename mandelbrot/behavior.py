# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
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

class DefaultBehavior(object):
    def __init__(self, **kwargs):
        self.scalar_flap_window = kwargs.get('scalar flap_window', None)
        self.scalar_flap_deviations = kwargs.get('scalar flap_deviations', None)
        self.aggregate_flap_window = kwargs.get('aggregate flap_window', None)
        self.aggregate_flap_deviations = kwargs.get('aggregate flap_deviations', None)
        self.metrics_flap_window = kwargs.get('metrics flap_window', None)
        self.metrics_flap_deviations = kwargs.get('metrics flap_deviations', None)

    def merge(self, override):
        if isinstance(override, ScalarBehavior):
            flap_window = override.flap_window if override.flap_window is not None else self.flap_window
            flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
            return ScalarBehavior(flap_window, flap_deviations)
        raise Exception()

class OverrideScalarBehavior(object):
    def __init__(self, **kwargs):
        self.flap_window = kwargs.get('flap_window', None)
        self.flap_deviations = kwargs.get('flap_deviations', None)

    def merge(self, override):
        flap_window = override.flap_window if override.flap_window is not None else self.flap_window
        flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
        return OverridePolicy(flap_window=flap_window, flap_deviations=flap_deviations)

class ScalarBehavior(object):
    def __init__(self, flap_window, flap_deviations):
        if flap_window is None:
            raise ValueError("flap_window cannot be None")
        if flap_deviations is None:
            raise ValueError("flap_deviations cannot be None")
        self.flap_window = flap_window
        self.flap_deviations = flap_deviations

    def merge(self, override):
        flap_window = override.flap_window if override.flap_window is not None else self.flap_window
        flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
        return ScalarBehavior(flap_window, flap_deviations)

    def __dump__(self):
        spec = dict()
        spec['behaviorType'] = "scalar"
        spec['behaviorPolicy'] = {"flapWindow": self.flap_window, "flapDeviations": self.flap_deviations}
        return spec

class OverrideAggregateBehavior(object):
    def __init__(self, **kwargs):
        self.flap_window = kwargs.get('flap_window', None)
        self.flap_deviations = kwargs.get('flap_deviations', None)

    def merge(self, override):
        flap_window = override.flap_window if override.flap_window is not None else self.flap_window
        flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
        return OverridePolicy(flap_window=flap_window, flap_deviations=flap_deviations)

class AggregateBehavior(object):
    def __init__(self, flap_window, flap_deviations):
        if flap_window is None:
            raise ValueError("flap_window cannot be None")
        if flap_deviations is None:
            raise ValueError("flap_deviations cannot be None")
        self.flap_window = flap_window
        self.flap_deviations = flap_deviations

    def merge(self, override):
        flap_window = override.flap_window if override.flap_window is not None else self.flap_window
        flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
        return AggregateBehavior(flap_window, flap_deviations)

    def __dump__(self):
        spec = dict()
        spec['behaviorType'] = "aggregate"
        spec['behaviorPolicy'] = {"flapWindow": self.flap_window, "flapDeviations": self.flap_deviations}
        return spec

class OverrideMetricsBehavior(object):
    def __init__(self, **kwargs):
        self.evaluation = kwargs.get('evaluation', None)
        self.flap_window = kwargs.get('flap_window', None)
        self.flap_deviations = kwargs.get('flap_deviations', None)

    def merge(self, override):
        evaluation = override.evaluation if override.evaluation is not None else self.evaluation
        flap_window = override.flap_window if override.flap_window is not None else self.flap_window
        flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
        return OverridePolicy(evaluation=evaluation, flap_window=flap_window, flap_deviations=flap_deviations)

class MetricsBehavior(object):
    def __init__(self, evaluation, flap_window, flap_deviations):
        if evaluation is None:
            raise ValueError("evaluation cannot be None")
        if flap_window is None:
            raise ValueError("flap_window cannot be None")
        if flap_deviations is None:
            raise ValueError("flap_deviations cannot be None")
        self.evaluation = evaluation
        self.flap_window = flap_window
        self.flap_deviations = flap_deviations

    def merge(self, override):
        evaluation = override.evaluation if override.evaluation is not None else self.evaluation
        flap_window = override.flap_window if override.flap_window is not None else self.flap_window
        flap_deviations = override.flap_deviations if override.flap_deviations is not None else self.flap_deviations
        return MetricsBehavior(evaluation, flap_window, flap_deviations)

    def __dump__(self):
        spec = dict()
        spec['behaviorType'] = "metrics"
        spec['behaviorPolicy'] = {"evaluation": self.evaluation, "flapWindow": self.flap_window, "flapDeviations": self.flap_deviations}
        return spec
