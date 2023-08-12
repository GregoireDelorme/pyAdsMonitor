import time
import json
import argparse
import configparser

from lib.bing import Bing

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ads Monitor tool")
    parser.add_argument("-c", "--config", help="Configuration file",  required=True)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)
    sections = config.sections()
    waiting_s = int(config['INIT']["wait_loop"])
    while True:
        for section in sections[1:]:
            print(f"Running Ads Monitor for {section}")
            search_engines = json.loads(config[section]["search_engines"])
            for search_engine in search_engines:
                se = globals()[search_engine.capitalize()](settings=(config, section))
                se.search()
            print(f"Waiting {waiting_s}s")
            time.sleep(waiting_s)
