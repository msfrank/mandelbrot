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

from mandelbrot.check import Check
from mandelbrot.model.evaluation import HEALTHY

class AlwaysHealthy(Check):
    """
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.check.ScalarCheck"

    def get_behavior(self):
        return {}

    def execute(self, evaluation, context):
        evaluation.set_health(HEALTHY)
        evaluation.set_summary("check returns healthy")
