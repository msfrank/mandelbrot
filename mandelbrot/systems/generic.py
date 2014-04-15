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
    def get_metadata(self):
        system, node, release, version, machine, processor = platform.uname()
        host_metadata = {
            'unameSystem': system,
            'unameNode': node,
            'unameRelease': release,
            'unameVersion': version,
            'unameMachine': machine,
            'unameProcessor': processor
        }
        if system.lower() == 'linux':
            distname,version,id = platform.linux_distribution()
            host_metadata['linuxDistname'] = distname
            host_metadata['linuxDistversion'] = version
            host_metadata['linuxDistId'] = id
        if system.lower() == 'darwin':
            release, versioninfo, machine = platform.mac_ver()
            host_metadata['appleRelease'] = release
            host_metadata['appleMachine'] = machine
            if versioninfo != '':
                version, dev_stage, non_release_version = versioninfo
                host_metadata['appleVersion'] = version
                host_metadata['appleDevstage'] = dev_stage
                host_metadata['appleNonReleaseVersion'] = non_release_version
        if system.lower() == 'windows':
            release, version, csd, ptype = platform.win32_ver
            host_metadata['windowsRelease'] = release
            host_metadata['windowsVersion'] = version
            host_metadata['windowsCSD'] = csd
            host_metadata['windowsPtype'] = ptype
        if system.lower() == 'java':
            pass
        else:
            pass
        metadata = System.get_metadata(self)
        metadata.update(host_metadata)
        return metadata

    def configure(self, section):
        System.configure(self, section)
        self.set_id("fqdn:" + socket.getfqdn())

    def describe(self):
        return None
