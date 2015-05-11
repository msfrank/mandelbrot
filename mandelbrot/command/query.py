import sys
import argparse
import traceback

import mandelbrot.command.query_condition

def main():
    """
    """
    try:

        # create the top-level parser
        parser = argparse.ArgumentParser(prog='mandelbrot-query')
        parser.set_defaults(main=lambda ns: 0)
        subparsers = parser.add_subparsers()

        query_condition = subparsers.add_parser('condition')
        query_condition.set_defaults(main=mandelbrot.command.query_condition.run_command)
        query_condition.add_argument('-i', '--agent-id', metavar='NAME', dest='agent_id')
        query_condition.add_argument('-u', '--endpoint-url', metavar='URL', dest='endpoint_url')
        query_condition.add_argument('-v', '--verbose', action='store_true')
        query_condition.add_argument('-p', '--pool-workers', metavar='NUM', dest='pool_workers',
                                    type=int, default=10, help='Size of the check worker pool')
        query_condition.add_argument('--log-level', metavar='LEVEL', dest='log_level',
                                    choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='INFO',
                                    help='Log at the specified level')
        query_condition.add_argument('check_id', metavar='CHECK')

        ns = parser.parse_args()
        return ns.main(ns)

    except Exception as e:
        print("\nUnhandled Exception:\n{0}\n---\n{1}".format(e,traceback.format_exc()), file=sys.stderr, flush=True)
        sys.exit(255)
