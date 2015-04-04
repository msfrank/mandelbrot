import sys
import traceback
import concurrent.futures
import logging

from mandelbrot.agent.supervisor import Supervisor

def main():
    """
    :return:
    """
    try:
        logging.basicConfig(level=logging.DEBUG)
        path = '/tmp'
        endpoint_url = 'http://localhost'
        endpoint_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        check_executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)
        supervisor = Supervisor(path, endpoint_url, endpoint_executor, check_executor)
        supervisor.run_forever()
    except Exception as e:
        print("\nUnhandled Exception:\n{0}\n---\n{1}".format(e,traceback.format_exc()), file=sys.stderr, flush=True)
        sys.exit(1)