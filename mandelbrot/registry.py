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
            working_set.add(plugin)
        for error in errors:
            log.info("failed to load distribution: %s", error)

    def lookup_check(self, check_type, requirement=None):
        """
        :param check_type:
        :type check_type: str
        :param requirement:
        :type requirement: pkg_resources.Requirement
        """
        entrypoint = None
        # find the entrypoint matching the specified requirement
        if requirement is not None:
            requirement = pkg_resources.Requirement.parse(requirement)
            distribution = working_set.find(requirement)
            entrypoint = distribution.load_entry_point('mandelbrot.check', check_type)
        # find the first entry point
        else:
            entrypoints = working_set.iter_entry_points('mandelbrot.check', check_type)
            try:
                entrypoint = entrypoints.next()
            except:
                pass
        if entrypoint is None:
            raise Exception("no check found named " + check_type)
        factory = entrypoint.load()
        log.debug("loaded factory %s", factory)
        return factory
