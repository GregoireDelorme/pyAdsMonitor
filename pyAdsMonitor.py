#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import argparse
import pathlib
import configparser

from lib.search_engine import Google, Bing
from lib.chrome import Launcher

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ads Monitor tool")
    parser.add_argument("-c", "--config", help="Configuration file", required=True, type=pathlib.Path)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    sections = config.sections()
    waiting_s = int(config['INIT']["wait_loop"])
    launcher = Launcher(config=config)
    while True:
        for section in sections[1:]:
            print(f"Running Ads Monitor for {section}")
            search_engines = json.loads(config[section]["search_engines"])
            for search_engine in search_engines:
                se = globals()[search_engine.capitalize()](launcher=launcher, section=section)
                se.search()
            print(f"Waiting {waiting_s}s")
            time.sleep(waiting_s)
