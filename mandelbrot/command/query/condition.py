import asyncio
import urllib.parse
import cifparser
import pprint
import logging

from mandelbrot.registry import Registry
from mandelbrot.query.endpoint import make_endpoint
from mandelbrot.log import utility_format

def run_command(ns):
    """
    """
    if ns.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format=utility_format)
    else:
        logging.basicConfig(level=logging.WARNING, format=utility_format)
    log = logging.getLogger('mandelbrot')

    event_loop = asyncio.get_event_loop()
    registry = Registry()

    endpoint_url = urllib.parse.urlparse(ns.endpoint_url)
    agent_id = cifparser.make_path(ns.agent_id)
    check_id = cifparser.make_path(ns.check_id)

    # construct the endpoint
    log.debug("constructing endpoint %s", endpoint_url)
    with make_endpoint(event_loop, endpoint_url, registry, 10) as endpoint:
        check_condition = event_loop.run_until_complete(endpoint.get_current_condition(agent_id, check_id))
        pprint.pprint(check_condition.destructure())
    return 0
