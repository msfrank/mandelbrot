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

entry_point_type = 'mandelbrot.check'

class Check(object):
    """
    """
    def __init__(self, ns, **kwargs):
        """
        :param ns:
        :type ns: cifparser.Namespace
        :return:
        """
        self.ns = ns

    def get_join_timeout(self):
        """
        The join timeout defines how long a check can remain in JOINING
        state before its health is considered UNKNOWN.
        """
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "join timeout")

    def get_check_timeout(self):
        """
        """
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "check timeout")

    def get_alert_timeout(self):
        """
        """
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "alert timeout")

    def get_retirement_age(self):
        """
        """
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "retirement age")

    def get_allowed_notifications(self):
        return self.ns.get_str_list_or_default(cifparser.ROOT_PATH, "allowed notifications")

    def get_metrics(self):
        """
        Return the set of metrics to register.
        """
        return {}

    def init(self):
        """
        Perform any initialization necessary before calling execute for
        the first time, and return the initial check context.
        """
        pass

    def fini(self, context):
        """
        Perform cleanup tasks before shutdown.
        """
        pass

    def get_behavior_type(self):
        """
        Return the server-side behavior.

        :rtype: str
        """
        raise NotImplementedError()

    def get_behavior(self):
        """

        :rtype: dict[str,str]
        """
        raise NotImplementedError()

    def execute(self, evaluation, context):
        """
        Execute the check, and return an Evaluation.

        :rtype: mandelbrot.model.Evaluation
        """
        raise NotImplementedError()
