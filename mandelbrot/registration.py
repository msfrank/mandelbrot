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

import pprint

class SystemRegistration(object):
    """
    """
    def __init__(self, system):
        self.system = system

    def __repr__(self):
        return str(self.__dump__())

    def __str__(self):
        return pprint.pformat(self.__dump__())

    def __dump__(self):
        systemtype = self.system.get_type()
        metadata = self.system.get_metadata()
        probes = {}
        for name,child in self.system.iter_probes():
            probes[name] = ProbeRegistration(child).__dump__()
        return {'systemType': self.system.get_type(), 'metadata': self.system.get_metadata(), 'probes': probes}

class ProbeRegistration(object):
    """
    """
    def __init__(self, probe):
        self.probe = probe
        self.children = dict()
        for name,child in probe.iter_probes():
            self.children[name] = ProbeRegistration(child)

    def __repr__(self):
        return str(self.__dump__())

    def __str__(self):
        return pprint.pformat(self.__dump__())

    def __dump__(self):
        probetype = self.probe.get_type()
        metadata = self.probe.get_metadata()
        policy = self.probe.get_policy().__dump__()
        behavior = self.probe.get_behavior().__dump__()
        children = dict()
        for name,child in self.probe.iter_probes():
            children[name] = child.__dump__()
        return {'probeType': probetype, 'metadata': metadata, 'policy': policy, 'behavior': behavior, 'children': children}

