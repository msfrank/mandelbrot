import asyncio
import urllib.parse
import cifparser
import pprint
import logging

from mandelbrot.registry import Registry
from mandelbrot.query.endpoint import make_endpoint
from mandelbrot.timerange import parse_timerange
from mandelbrot.table import Table, Column, Rowstore, Terminal
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

    agent_id = cifparser.make_path(ns.agent_id)
    check_id = cifparser.make_path(ns.check_id)
    if ns.timerange:
        timerange = parse_timerange(ns.timerange)
    else:
        timerange = None
    limit = ns.limit
    reverse = ns.reverse
    endpoint_url = urllib.parse.urlparse(ns.endpoint_url)

    # construct the endpoint
    log.debug("constructing endpoint %s", endpoint_url)
    with make_endpoint(event_loop, endpoint_url, registry, 10) as endpoint:

        # query the endpoint, store the results in rowstore
        rowstore = Rowstore()
        if timerange:
            nleft = limit
            last = None
            while nleft > 0:
                coro = endpoint.list_conditions(agent_id, check_id, nleft,
                    start=timerange[0], end=timerange[1], last=last, descending=reverse)
                page = event_loop.run_until_complete(coro)
                for check_condition in page.list_check_conditions():
                    rowstore.append_row(check_condition.destructure())
                last = page.get_last()
                if page.get_exhausted():
                    break
        else:
            coro = endpoint.get_current_condition(agent_id, check_id)
            check_condition = event_loop.run_until_complete(coro)
            rowstore.append_row(check_condition.destructure())

        # render the rowstore in a table
        table = Table()
        terminal = Terminal()
        table.append_column(Column('Timestamp', 'timestamp', normalize=False))
        table.append_column(Column('Lifecycle', 'lifecycle', normalize=False))
        table.append_column(Column('Health', 'health', normalize=False))
        table.append_column(Column('Summary', 'summary', expand=True))
        table.append_column(Column('Acknowledged', 'acknowledged', normalize=False))
        table.append_column(Column('Squelched', 'squelched', normalize=False))
        table.print_table(rowstore, terminal)

    return 0
