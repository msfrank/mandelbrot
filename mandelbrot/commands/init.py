import pathlib
import logging

from mandelbrot.instance import create_instance
from mandelbrot.commands import utility_format

def init_main(ns):
    """
    """
    if ns.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format=utility_format)
    else:
        logging.basicConfig(level=logging.INFO, format=utility_format)
    log = logging.getLogger('mandelbrot')

    agent_id = ns.agent_id
    endpoint_url = ns.endpoint_url
    instance = create_instance(pathlib.Path(ns.path))

    with instance.lock():
        instance.set_agent_id(agent_id)
        instance.set_endpoint_url(endpoint_url)
    return 0
