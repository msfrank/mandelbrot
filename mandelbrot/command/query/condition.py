import asyncio
import urllib.parse
import cifparser
import logging

from mandelbrot.registry import Registry
from mandelbrot.query.endpoint import make_endpoint
from mandelbrot.timerange import parse_timerange
from mandelbrot.table import Table, Column, Rowstore, Terminal, maybe
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
    if ns.sort_columns:
        sort_columns = [column.lower().strip() for column in ns.sort_columns.split(',')]
    else:
        sort_columns = None
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
                    rowstore.append_row(check_condition_to_row(check_condition))
                    nleft -= 1
                last = page.get_last()
                if page.get_exhausted():
                    break
        else:
            coro = endpoint.get_current_condition(agent_id, check_id)
            check_condition = event_loop.run_until_complete(coro)
            rowstore.append_row(check_condition_to_row(check_condition))

        # sort the rowstore if sort columns are specified
        if sort_columns:
            rowstore.sort_rows(sort_columns, False)

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

def check_condition_to_row(check_condition):
    """
    :param check_condition:
    :type check_condition: CheckCondition
    :return:
    """
    return {
        'timestamp': check_condition.get_timestamp().get_datetime().isoformat(),
        'lifecycle': check_condition.get_lifecycle(),
        'health': check_condition.get_health(),
        'summary': maybe(check_condition.get_summary()),
        'acknowledged': maybe(check_condition.get_acknowledged()),
        'squelched': 'on' if check_condition.get_squelched() else '',
    }
