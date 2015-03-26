import sys, os
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s: %(message)s")
