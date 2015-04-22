import pkg_resources
import logging

log = logging.getLogger("mandelbrot.registry")

from mandelbrot import versionstring
require_mandelbrot = 'mandelbrot == ' + versionstring()

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

    def lookup_factory(self, entry_point_type, factory_name, factory_type, requirement=require_mandelbrot):
        """
        :param entry_point_type:
        :type entry_point_type: str
        :param factory_name:
        :type factory_name: str
        :param factory_type:
        :type factory_type: type
        :param requirement:
        :type requirement: str
        """
        # find the entrypoint matching the specified requirement
        requirement = pkg_resources.Requirement.parse(requirement)
        distribution = pkg_resources.working_set.find(requirement)
        factory = distribution.load_entry_point(entry_point_type, factory_name)
        log.debug("loaded factory %s.%s", factory.__module__, factory.__class__.__name__)
        if not issubclass(factory, factory_type):
            raise TypeError("{}.{} is not a subclass of {}".format(
                factory.__module__, factory.__class__.__name__, factory_type.__name__))
        return factory
