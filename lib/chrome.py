import os
import shutil
import subprocess

from glob import glob

import undetected_chromedriver as uc


class Launcher:
    driver = None
    ph_site_list = list()
    settings = None
    pb = None

    def __init__(self, config):

        self.close_all()
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument(f"--user-data-dir={os.path.dirname(__file__)}/../chrome-data-dir")
        chrome_options.add_argument(f'--homedir={os.path.dirname(__file__)}/../chrome-data-dir')
        self.driver = uc.Chrome(headless=True, options=chrome_options)
        self.config = config

        if "pushbullet_key_api" in self.config["INIT"] and self.config["INIT"]["pushbullet_key_api"]:
            from pushbullet import Pushbullet
            self.pb = Pushbullet(self.config["INIT"]["pushbullet_key_api"])

    def close_all(self):
        p = glob(f'{os.path.dirname(__file__)}/../chrome-data-dir/*')
        for d in p:
            try:
                shutil.rmtree(d)
            except Exception as e:
                pass
        try:
            subprocess.run(["killall", "undetected_chromedriver"], timeout=5)
            subprocess.run(["killall", "chrome"], timeout=5)
        except Exception as e:
            pass
