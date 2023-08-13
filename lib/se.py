from datetime import datetime
from urllib.parse import urlparse

import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class AdsMonitor:
    driver = None
    ph_site_list = list()
    settings = None
    pb = None

    def __init__(self, settings):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        self.driver = uc.Chrome(headless=True)
        self.config, self.section = settings
        self.settings = self.config[self.section]
        if "pushbullet_key_api" in settings and settings["pushbullet_key_api"]:
            from pushbullet import Pushbullet
            self.pb = Pushbullet(self.config["INIT"]["pushbullet_key_api"])

    def wait_for_elements(self, element, css):
        wait = WebDriverWait(self.driver, 2)
        try:
            wait.until(ec.visibility_of_all_elements_located((By.CSS_SELECTOR, css)))
            return element.find_elements(By.CSS_SELECTOR, css)
        except Exception as e:
            return []

    def get_ph_site(self, url):
        self.driver.get(url)
        date = datetime.now().strftime("%m-%d-%Y_%Hh%M")
        page = self.wait_for_elements(self.driver, "body")
        site_url = self.driver.current_url
        parsed_domain = AdsMonitor.get_domain_from_url(site_url)
        self.screenshot(page[0], f'ph_{parsed_domain}')
        return site_url

    def screenshot(self, element, name):
        date = datetime.now().strftime("%m-%d-%Y_%Hh%M")
        element.screenshot(f'{date}_{name}.png')

    @staticmethod
    def get_domain_from_url(url):
        return '.'.join(urlparse(url).netloc.split('.')[-2:])
