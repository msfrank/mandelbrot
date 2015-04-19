from mandelbrot.checks import Check
from mandelbrot.model.evaluation import Evaluation, HEALTHY

class AlwaysHealthy(Check):
    """
    """
    def get_behavior_type(self):
        return "io.mandelbrot.core.system.ScalarProbe"

    def get_behavior(self):
        return {}

    def execute(self):
        evaluation = Evaluation()
        evaluation.set_summary("check returns healthy")
        evaluation.set_health(HEALTHY)
        return evaluation
