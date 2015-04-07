import logging
import pkg_resources

log = logging.getLogger("mandelbrot.registry")

class Registry(object):
    """
    """
    def __init__(self):
        self.env = pkg_resources.Environment([])
        plugins,errors = pkg_resources.working_set.find_plugins(self.env)
        for plugin in plugins:
            pkg_resources.working_set.add(plugin)
        for error in errors:
            log.info("failed to load distribution: %s", error)

    def lookup_check(self, check_type, requirement=None):
        """
        :param check_type:
        :type check_type: str
        :param requirement:
        :type requirement: str
        """
        # find the entrypoint matching the specified requirement
        if requirement is not None:
            requirement = pkg_resources.Requirement.parse(requirement)
            distribution = pkg_resources.working_set.find(requirement)
            factory = distribution.load_entry_point('mandelbrot.check', check_type)
        # find the first entry point
        else:
            entrypoints = pkg_resources.working_set.iter_entry_points('mandelbrot.check', check_type)
            try:
                factory = next(entrypoints).load()
            except:
                raise Exception("no check found named " + check_type)
        log.debug("loaded factory %s", factory)
        return factory
