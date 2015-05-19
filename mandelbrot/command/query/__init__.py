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

import sys
import argparse
import traceback

def main():
    """
    """
    try:
        import mandelbrot.command.query.condition as condition
        import mandelbrot.command.query.notifications as notifications
        import mandelbrot.command.query.metrics as metrics

        # create the top-level parser
        parser = argparse.ArgumentParser(prog='mandelbrot-query')
        parser.set_defaults(main=lambda ns: 0)
        subparsers = parser.add_subparsers()

        # query condition
        query_condition = subparsers.add_parser('condition')
        query_condition.set_defaults(main=condition.run_command)
        query_condition.add_argument('-i', '--agent-id', metavar='AGENT', dest='agent_id',
                                     help='Query the specified AGENT')
        query_condition.add_argument('-t', '--timerange', metavar='TIMERANGE', dest='timerange', default=None,
                                     help='Request results within the specified TIMERANGE')
        query_condition.add_argument('-l', '--limit', metavar='LIMIT', dest='limit', type=int, default=100,
                                     help='Return at most LIMIT results')
        query_condition.add_argument('-s', '--sort-by', metavar='COLUMNS', dest='sort_columns', default=None,
                                     help='Sort results using the specified COLUMNS')
        query_condition.add_argument('-r', '--reverse', dest='reverse', action='store_true',
                                     help='Return results in descending order')
        query_condition.add_argument('-u', '--endpoint-url', metavar='URL', dest='endpoint_url',
                                     help="Query the specified endpoint URL")
        query_condition.add_argument('-v', '--verbose', action='store_true')
        query_condition.add_argument('-p', '--pool-workers', metavar='NUM', dest='pool_workers',
                                    type=int, default=10, help='Size of the query worker pool')
        query_condition.add_argument('--log-level', metavar='LEVEL', dest='log_level',
                                    choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='INFO',
                                    help='Log at the specified level')
        query_condition.add_argument('check_id', metavar='CHECK')

        # query notifications
        query_notifications = subparsers.add_parser('notifications')
        query_notifications.set_defaults(main=notifications.run_command)
        query_notifications.add_argument('-i', '--agent-id', metavar='AGENT', dest='agent_id',
                                     help='Query the specified AGENT')
        query_notifications.add_argument('-t', '--timerange', metavar='TIMERANGE', dest='timerange', default=None,
                                     help='Request results within the specified TIMERANGE')
        query_notifications.add_argument('-l', '--limit', metavar='LIMIT', dest='limit', type=int, default=100,
                                     help='Return at most LIMIT results')
        query_notifications.add_argument('-r', '--reverse', dest='reverse', action='store_true',
                                     help='Return results in descending order')
        query_notifications.add_argument('-u', '--endpoint-url', metavar='URL', dest='endpoint_url',
                                     help="Query the specified endpoint URL")
        query_notifications.add_argument('-v', '--verbose', action='store_true')
        query_notifications.add_argument('-p', '--pool-workers', metavar='NUM', dest='pool_workers',
                                    type=int, default=10, help='Size of the query worker pool')
        query_notifications.add_argument('--log-level', metavar='LEVEL', dest='log_level',
                                    choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='INFO',
                                    help='Log at the specified level')
        query_notifications.add_argument('check_id', metavar='CHECK')

        # query metrics
        query_metrics = subparsers.add_parser('metrics')
        query_metrics.set_defaults(main=metrics.run_command)
        query_metrics.add_argument('-i', '--agent-id', metavar='AGENT', dest='agent_id',
                                         help='Query the specified AGENT')
        query_metrics.add_argument('-t', '--timerange', metavar='TIMERANGE', dest='timerange', default=None,
                                         help='Request results within the specified TIMERANGE')
        query_metrics.add_argument('-l', '--limit', metavar='LIMIT', dest='limit', type=int, default=100,
                                         help='Return at most LIMIT results')
        query_metrics.add_argument('-r', '--reverse', dest='reverse', action='store_true',
                                         help='Return results in descending order')
        query_metrics.add_argument('-u', '--endpoint-url', metavar='URL', dest='endpoint_url',
                                         help="Query the specified endpoint URL")
        query_metrics.add_argument('-v', '--verbose', action='store_true')
        query_metrics.add_argument('-p', '--pool-workers', metavar='NUM', dest='pool_workers',
                                         type=int, default=10, help='Size of the query worker pool')
        query_metrics.add_argument('--log-level', metavar='LEVEL', dest='log_level',
                                         choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='INFO',
                                         help='Log at the specified level')
        query_metrics.add_argument('check_id', metavar='CHECK')

        ns = parser.parse_args()
        return ns.main(ns)

    except Exception as e:
        print("\nUnhandled Exception:\n{0}\n---\n{1}".format(e,traceback.format_exc()), file=sys.stderr, flush=True)
        sys.exit(255)
