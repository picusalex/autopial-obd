#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import threading

import time
import sys

import os
from obd import obd

from autopial_lib.thread_worker import AutopialWorker
from autopial_lib.config_driver import ConfigFile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
steam_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('%(asctime)s|%(levelname)08s | %(message)s')
steam_handler.setFormatter(stream_formatter)
logger.addHandler(steam_handler)

OBD_LOCK = threading.Lock()
obd_connection = None

class OBDWorker(AutopialWorker):
    def __init__(self, mqtt_client, time_sleep, obd_ids):
        AutopialWorker.__init__(self, mqtt_client, time_sleep, logger=logger)
        self.obd_ids = obd_ids

    def run(self):
        logger.info("OBDWorker thread starts")
        while self.wait():
            self.get_obd_value("ELM_VOLTAGE")
            print("test {}, {}".format(self.name, self.obd_ids))
            continue


            topic = "autopial/system/swap"
            data = psutil.swap_memory()
            value = {
                "free": data.free,
                "total": data.total,
                "used": data.used,
                "usage": float(data.used) / float(data.total) * 100.0
            }
            self.publish(topic, value)
        logger.info("OBDWorker thread ends")

    def get_obd_value(self, id):
        result = obd_connection.query(id)
        pass

if __name__ == '__main__':
    cfg = ConfigFile("autopial-obd.cfg", logger=logger)
    try:
        port = cfg.get("obd_device", "port")
        baudrate = cfg.get("obd_device", "baudrate")

        fast_publish_every = cfg.get("workers", "FastWorker", "publish_every")
        fast_ids = cfg.get("workers", "FastWorker", "ids")

        slow_publish_every = cfg.get("workers", "SlowWorker", "publish_every")
        slow_ids = cfg.get("workers", "SlowWorker", "ids")
    except BaseException as e:
        logger.error("Invalid config file: {}".format(e))
        sys.exit(1)

    if not os.path.exists(port):
        logger.error("Specified OBD port '{}' does not exists !".format(port))
        sys.exit(1)

    obd_connection = obd.OBD(portstr=port, baudrate=baudrate, timeout=1)

    fastworker_obd = OBDWorker("FastWorker", time_sleep=fast_publish_every, obd_ids=fast_ids)
    fastworker_obd.start()

    slowworker_obd = OBDWorker("SlowWorker", time_sleep=slow_publish_every, obd_ids=slow_ids)
    slowworker_obd.start()

    try:
        while 1:
            time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        fastworker_obd.stop()
        slowworker_obd.stop()



