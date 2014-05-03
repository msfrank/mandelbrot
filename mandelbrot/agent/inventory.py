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

from pesky.settings import ConfigureError
from twisted.persisted.dirdbm import DirDBM
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.inventory')

class InventoryDatabase(object):
    """
    Manages inventory objects as a tree, with the system as the root, 
    and probes forming branches and leaves.
    """
    def __init__(self, plugins, state):
        self.plugins = plugins
        self.state = state
        self.root = None

    def configure(self, ns):
        # initialize the root
        section = ns.get_section('system')
        roottype = section.get_str('system type')
        logger.debug("creating %s system", roottype)
        try:
            self.root = self.plugins.newinstance('io.mandelbrot.system', roottype)
        except Exception, e:
            raise ConfigureError("failed to configure system: %s" % e)
        self.root.configure(section)
        logger.debug("configured system %s", self.root.get_id())
        # initialize each probe specified in the configuration
        for section in sorted(ns.find_sections('probe:'), key=lambda k: k.name):
            try:
                probepath = section.name[6:]
                if not probepath.startswith('/'):
                    raise Exception("probe path must start with /")
                logger.debug("creating probe %s", probepath)
                parentpath,probename = probepath.rsplit('/', 1)
                if parentpath == '':
                    parent = self.get_object('/')
                else:
                    parent = self.get_object(parentpath)
                if parent is None:
                    raise Exception("no parent probe found for %s" % probepath)
                probetype = section.get_str('probe type')
                if probetype is None:
                    raise Exception("no probe type found for %s" % probetype)
                probe = self.plugins.newinstance('io.mandelbrot.probe', probetype)
                probe.id = probename
                probe.configure(section)
                # register probe as an inventory object
                parent[probename] = probe
                logger.debug("configured probe %s", probepath)
            except ConfigureError, e:
                raise
            except Exception, e:
                logger.warning("skipping section %s: %s", section.name, str(e))

    def get_object(self, path):
        """
        Return the object specified by the object path, or None if the object
        doesn't exist.
        """
        def find_object(o, segments):
            if len(segments) == 0:
                return o
            curr = segments[0]
            if curr in o:
                return find_object(o[curr], segments[1:])
            return None
        if not path.startswith('/'):
            raise Exception("object path must be absolute")
        if path == '/':
            return self.root
        return find_object(self.root, path[1:].split('/'))

    @property
    def spec(self):
        def makespec(obj):
            children = {}
            for name,child in obj.children.items():
                children[name] = makespec(child)
            return {'objectType': obj.get_type(), 'metaData': obj.get_metadata(), 'children': children}
        return makespec(self.root)

    @property
    def uri(self):
        return self.root.get_id()
