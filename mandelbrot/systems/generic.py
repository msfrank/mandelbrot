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

import os, platform, socket
from mandelbrot.systems import System

class GenericHost(System):
    """
    """
    def configure(self, systemtype, settings, metadata, policy):
        uri = settings.get_str("uri", "fqdn:" + socket.getfqdn())
        system, node, release, version, machine, processor = platform.uname()
        _metadata = {
            'unameSystem': system,
            'unameNode': node,
            'unameRelease': release,
            'unameVersion': version,
            'unameMachine': machine,
            'unameProcessor': processor
        }
        if system.lower() == 'linux':
            distname,version,id = platform.linux_distribution()
            _metadata['linuxDistname'] = distname
            _metadata['linuxDistversion'] = version
            _metadata['linuxDistId'] = id
        if system.lower() == 'darwin':
            release, versioninfo, machine = platform.mac_ver()
            _metadata['appleRelease'] = release
            _metadata['appleMachine'] = machine
            if versioninfo != '':
                version, dev_stage, non_release_version = versioninfo
                _metadata['appleVersion'] = version
                _metadata['appleDevstage'] = dev_stage
                _metadata['appleNonReleaseVersion'] = non_release_version
        if system.lower() == 'windows':
            release, version, csd, ptype = platform.win32_ver
            _metadata['windowsRelease'] = release
            _metadata['windowsVersion'] = version
            _metadata['windowsCSD'] = csd
            _metadata['windowsPtype'] = ptype
        if system.lower() == 'java':
            pass
        else:
            pass
        _metadata.update(metadata)
        System.configure(self, uri, systemtype, _metadata, policy)
