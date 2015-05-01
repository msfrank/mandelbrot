from mandelbrot.check import Check
from mandelbrot.model.evaluation import HEALTHY

class AlwaysHealthy(Check):
    """
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def execute(self, evaluation, context):
        evaluation.set_health(HEALTHY)
        evaluation.set_summary("check returns healthy")
