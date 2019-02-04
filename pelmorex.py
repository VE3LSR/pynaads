#!/usr/bin/env python3

import colorlog
import logging
import pynaads

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
logger.info("Test")
p = pynaads.naads(passhb=True)
p.connect()
p.start()

while True:
    item = p.getQueue()
    if item:
        logger.debug(item.prettify())
