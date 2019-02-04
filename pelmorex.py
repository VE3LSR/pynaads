#!/usr/bin/env python3

import colorlog
import pynaads

logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
logger.info("Test")
p = naads()
p.connect()
p.start()

