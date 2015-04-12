import sys
import argparse
import traceback

import mandelbrot.agent.command

def main():
    """
    :return:
    """
    try:

        # create the top-level parser
        parser = argparse.ArgumentParser(prog='mandelbrot')
        parser.set_defaults(main=lambda ns: 0)
        subparsers = parser.add_subparsers()

        create_instance = subparsers.add_parser('create')
        create_instance.set_defaults(main=mandelbrot.agent.command.create_command)
        create_instance.add_argument('-i', '--agent-id', metavar='NAME', dest='agent_id')
        create_instance.add_argument('-u', '--endpoint-url', metavar='URL', dest='endpoint_url')
        create_instance.add_argument('-v', '--verbose', action='store_true')
        create_instance.add_argument('path', metavar='PATH')

        start_instance = subparsers.add_parser('start')
        start_instance.set_defaults(main=mandelbrot.agent.command.start_command)
        start_instance.add_argument('-f', '--foreground', action='store_true')
        start_instance.add_argument('-v', '--verbose', action='store_true')
        start_instance.add_argument('path', metavar='PATH')

        stop_instance = subparsers.add_parser('stop')
        stop_instance.set_defaults(main=mandelbrot.agent.command.stop_command)
        stop_instance.add_argument('-v', '--verbose', action='store_true')
        stop_instance.add_argument('path', metavar='PATH')

        ns = parser.parse_args()
        return ns.main(ns)


    except Exception as e:
        print("\nUnhandled Exception:\n{0}\n---\n{1}".format(e,traceback.format_exc()), file=sys.stderr, flush=True)
        sys.exit(1)