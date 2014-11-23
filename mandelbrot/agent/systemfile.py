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

import os, yaml
from ConfigParser import RawConfigParser
from pesky.settings.section import Section
from mandelbrot.loggers import getLogger

logger = getLogger('mandelbrot.agent.systemfile')

class SystemFile(object):
    def __init__(self, path, stream, doc):
        self.path = path
        self.stream = stream
        self.doc = doc

def parse_systemdir(systemdir):
    """
    """
    files = set(iter(filter(lambda f: f.endswith('.yaml'), os.listdir(systemdir))))
    systemfiles = list()
    # parse default system file
    if 'system.yaml' in files:
        files.remove('system.yaml')
        path = os.path.join(systemdir, 'system.yaml')
        with open(path, 'r') as f:
            streams = list(yaml.load_all(f))
            if len(streams) > 0:
                for i in range(len(streams)):
                    systemfiles.append(SystemFile(path, i, streams[i]))
            else:
                logger.warning("no systems found in system.yaml")
    else:
        logger.info("no system.yaml system file was found")
    # parse all remaining system files
    for systemfile in files:
        path = os.path.join(systemdir, systemfile)
        with open(path, 'r') as f:
            streams = list(yaml.load_all(f))
            if len(streams) > 0:
                for i in range(len(streams)):
                    systemfiles.append(SystemFile(path, i, streams[i]))
            else:
                logger.warning("no systems found in %s", systemfile)
    return systemfiles

class SystemSpec(object):
    def __init__(self, systemtype, settings, metadata, policy, probes):
        self.systemtype = systemtype
        self.settings = settings
        self.metadata = metadata
        self.policy = policy
        self.probes = probes

class ProbeSpec(object):
    def __init__(self, path, probetype, settings, metadata, policy, probes):
        self.path = path
        self.probetype = probetype
        self.settings = settings
        self.metadata = metadata
        self.policy = policy
        self.probes = probes

def parse_systemfile(systemfile):
    """
    """
    system = systemfile.doc["system"]
    system_type = system.pop("system type", None)
    # system metadata
    if "metadata" in system:
        system_metadata = dict()
        for k,v in system.pop("metadata").items():
            system_metadata[str(k)] = str(v)
    else:
        system_metadata = dict()
    # system policy
    options = RawConfigParser()
    options.add_section("policy")
    for k,v in system.pop("policy", dict()).items():
        options.set("policy", str(k), str(v))
    system_policy = Section("policy", options, os.path.dirname(systemfile.path))
    # system probes
    def parse_probe(probename, probe, parentname, parent):
        probe_path = parentname + probename
        probename = probename[1:]
        probe_type = probe.pop("probe type", None)
        options = RawConfigParser()
        # probe metadata
        if "metadata" in probe:
            probe_metadata = dict()
            for k,v in probe.pop("metadata").items():
                probe_metadata[str(k)] = str(v)
        else:
            probe_metadata = dict()
        # probe policy
        options = RawConfigParser()
        options.add_section("policy")
        for k,v in probe.pop("policy", dict()).items():
            options.set("policy", str(k), str(v))
        probe_policy = Section("policy", options, os.path.dirname(systemfile.path))
        # probe settings
        options = RawConfigParser()
        options.add_section("settings")
        for k in filter(lambda k: not k.startswith("/"), probe.keys()):
            options.set("settings", str(k), str(probe.pop(k)))
        probe_settings = Section("settings", options, os.path.dirname(systemfile.path))
        # probe children
        children = dict()
        for childname,childprobe in probe.items():
            parse_probe(childname, childprobe, probe_path, children)
        parent[probename] = ProbeSpec(probe_path, probe_type, probe_settings, probe_metadata, probe_policy, children)
    system_probes = dict()
    for childname,childprobe in system.pop("probes").items():
        if not childname.startswith("/"):
            raise Exception("expected probe, found %s", childname)
        parse_probe(childname, childprobe, "", system_probes)
    # system settings
    options = RawConfigParser()
    options.add_section("settings")
    for k,v in system.items():
        options.set("settings", str(k), str(v))
    system_settings = Section("settings", options, os.path.dirname(systemfile.path))
    # return system specification
    return SystemSpec(system_type, system_settings, system_metadata, system_policy, system_probes)
