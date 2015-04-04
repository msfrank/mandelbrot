from mandelbrot.checks import Check
from mandelbrot.model.evaluation import Evaluation, HEALTHY

class AlwaysHealthy(Check):
    """
    """
    def execute(self):
        return Evaluation(health=HEALTHY, summary="check returns healthy")
