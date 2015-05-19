# Copyright 2015 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import urllib.parse
import cifparser
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
                coro = endpoint.list_metrics(agent_id, check_id, nleft,
                                                   start=timerange[0], end=timerange[1], last=last, descending=reverse)
                page = event_loop.run_until_complete(coro)
                for check_metrics in page.list_check_metrics():
                    rowstore.append_row(metrics_to_row(check_metrics))
                    nleft -= 1
                last = page.get_last()
                if page.get_exhausted():
                    break
        else:
            coro = endpoint.get_current_metrics(agent_id, check_id)
            check_metrics = event_loop.run_until_complete(coro)
            rowstore.append_row(metrics_to_row(check_metrics))

        # render the rowstore in a table
        table = Table()
        terminal = Terminal()
        table.append_column(Column('Timestamp', 'timestamp', normalize=False))
        for field in rowstore.get_columns():
            if field == 'timestamp':
                continue
            table.append_column(Column(field, field, normalize=False))
        table.print_table(rowstore, terminal)

    return 0

def metrics_to_row(metrics):
    """
    :param metrics:
    :type metrics: CheckMetrics
    :return:
    """
    row = {
        'timestamp': metrics.get_timestamp().get_datetime().isoformat(),
    }
    for name,value in metrics.list_metrics():
        row[name] = value
    return row

