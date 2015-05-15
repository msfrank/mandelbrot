import sys
import argparse
import traceback

def main():
    """
    """
    try:
        import mandelbrot.command.agent.init as init
        import mandelbrot.command.agent.start as start
        import mandelbrot.command.agent.status as status
        import mandelbrot.command.agent.stop as stop

        # create the top-level parser
        parser = argparse.ArgumentParser(prog='mandelbrot')
        parser.set_defaults(main=lambda ns: 0)
        subparsers = parser.add_subparsers()

        init_instance = subparsers.add_parser('init')
        init_instance.set_defaults(main=init.run_command)
        init_instance.add_argument('-i', '--agent-id', metavar='NAME', dest='agent_id')
        init_instance.add_argument('-m', '--manifest', metavar='PATH', dest='manifest_path')
        init_instance.add_argument('-u', '--endpoint-url', metavar='URL', dest='endpoint_url')
        init_instance.add_argument('-v', '--verbose', action='store_true')
        init_instance.add_argument('path', metavar='PATH')

        start_instance = subparsers.add_parser('start')
        start_instance.set_defaults(main=start.run_command)
        start_instance.add_argument('-p', '--pool-workers', metavar='NUM', dest='pool_workers',
                                    type=int, default=10, help='Size of the check worker pool')
        start_instance.add_argument('-l', '--log-file', metavar='PATH', dest='log_file',
                                    help='Log to the specified file')
        start_instance.add_argument('--log-level', metavar='LEVEL', dest='log_level',
                                    choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], default='INFO',
                                    help='Log at the specified level')
        start_instance.add_argument('-f', '--foreground', action='store_true', dest='foreground',
                                    help='Run agent process in the foreground')
        start_instance.add_argument('-d', '--debug', action='store_true', dest='debug',
                                    help='Log at DEBUG level and write to stdout')
        start_instance.add_argument('path', metavar='PATH')

        instance_status = subparsers.add_parser('status')
        instance_status.set_defaults(main=status.run_command)
        instance_status.add_argument('-v', '--verbose', action='store_true')
        instance_status.add_argument('path', metavar='PATH')

        stop_instance = subparsers.add_parser('stop')
        stop_instance.set_defaults(main=stop.run_command)
        stop_instance.add_argument('-v', '--verbose', action='store_true')
        stop_instance.add_argument('path', metavar='PATH')

        ns = parser.parse_args()
        return ns.main(ns)

    except Exception as e:
        print("\nUnhandled Exception:\n{0}\n---\n{1}".format(e,traceback.format_exc()), file=sys.stderr, flush=True)
        sys.exit(255)
