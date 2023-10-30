import time
import json
import os

from datetime import datetime, timedelta
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class SearchEngine:
    driver = None
    ph_site_list = list()
    config = None
    settings = None
    pb = None

    def __init__(self, launcher, section):
        self.driver = launcher.driver
        self.config = launcher.config
        self.settings = self.config[section]

    def wait_for_elements(self, element, selector: str, selector_type: str = By.XPATH):
        wait = WebDriverWait(self.driver, 3)
        try:
            wait.until(ec.element_to_be_clickable((selector_type, selector)))
            return element.find_elements(selector_type, selector)
        except Exception as e:
            return []

    def get_ph_site(self, url: str):
        self.driver.get(url)
        page = self.wait_for_elements(self.driver, "//body")
        site_url = self.driver.current_url
        parsed_domain = SearchEngine.get_domain_from_url(site_url)
        SearchEngine.take_screenshot(page[0], f'ph_{parsed_domain}')
        return site_url

    def send_pushbullet(self):
        if self.pb and self.ph_site_list:
            for ph_site in self.ph_site_list:
                self.pb.push_note(
                    "Suspect Ads detected",
                    "\n".join([f"{k}: {v}" for k, v in ph_site.items()])
                )

    @staticmethod
    def take_screenshot(element, name: str):
        date = datetime.now().strftime("%m-%d-%Y_%Hh%M")
        element.take_screenshot(f'{os.path.dirname(__file__)}/../ads-data/{date}_{name}.png')

    @staticmethod
    def get_domain_from_url(url: str) -> str:
        return '.'.join(urlparse(url).netloc.split('.')[-2:])

    def is_old_domain(self, domain):
        if "check_whois_days" in self.config["INIT"] and self.config["INIT"]["check_whois_days"]:
            try:
                import whoisdomain as whois
                d = whois.query(domain)
                past = datetime.now() - timedelta(days=int(self.config["INIT"]["check_whois_days"]))
                if d.creation_date < past:
                    return True
                return False
            except Exception as e:
                return False
        return False


class Bing(SearchEngine):

    def __init__(self, launcher, section):
        SearchEngine.__init__(self, launcher, section)

    def search_ad(self, ad, keyword: str):
        page = self.wait_for_elements(self.driver, "//body")
        ele1 = self.wait_for_elements(ad, "//h2//a")
        ele2 = self.wait_for_elements(ad, "//[contains(@class,'b_adurl')]//a")
        if ele2 and ele1 and ele2[0].text != '':
            ad_site_url = ele2[0].text
            parsed_domain = SearchEngine.get_domain_from_url(ad_site_url)
            is_suspect = True if parsed_domain not in json.loads(self.settings["whitelist_domains"]) else False
            if is_suspect and not self.is_old_domain(parsed_domain):
                ph_site = {
                    "se": __class__.__name__,
                    "keyword": keyword,
                    "ad_site_url": ad_site_url,
                    "ad_site_domain": parsed_domain,
                    "ad_url": ele1[0].get_attribute('href'),
                    "ad_text": ele1[0].text,
                }
                self.driver.execute_script(
                    """
                    var l = document.getElementsByClassName("bnp_cookie_banner")[0];
                    if(l) {l.parentNode.removeChild(l);}
                    """
                )
                print(f"Suspected Ads: {ph_site['ad_site_url']}")
                self.take_screenshot(page[0], f'{keyword.replace(" ", "-")}_{parsed_domain}')
                ph_url = self.get_ph_site(ph_site['ad_url'])
                ph_site.update({"ph_url": ph_url})
                self.ph_site_list.append(ph_site)

    def search(self):
        for keyword in json.loads(self.settings["se_keywords"]):
            time.sleep(1)
            print(f"Searching on {__class__.__name__} for '{keyword}'")
            self.driver.get(f'https://www.bing.com/search?q={keyword}')
            self.driver.execute_script(
                """
                var l = document.getElementsByClassName("bnp_cookie_banner")[0];
                if(l) {l.parentNode.removeChild(l);};
                document.getElementsByTagName("html")[0].style.scrollBehavior = "auto";
                """
            )
            ads = self.wait_for_elements(
                self.driver,
                "//li[contains(@class,'b_adTop')]//ul//li//div[contains(@class,'sb_add')]"
            )
            for ad in ads:
                self.search_ad(ad, keyword)
        self.send_pushbullet()


class Google(SearchEngine):

    def __init__(self, launcher, section):
        SearchEngine.__init__(self, launcher, section)

    def search_ad(self, ad, keyword: str):
        page = self.wait_for_elements(self.driver, "//body")
        ele1 = self.wait_for_elements(ad, "div[role='heading'] span", By.CSS_SELECTOR)  # Utiliser xpath...
        ele2 = self.wait_for_elements(ad, "//a")
        if ele2 and ele1:
            ad_site_url = ele2[0].get_attribute('href')
            parsed_domain = SearchEngine.get_domain_from_url(ad_site_url)
            is_suspect = True if parsed_domain not in json.loads(self.settings["whitelist_domains"]) else False
            if is_suspect and not self.is_old_domain(parsed_domain):
                ph_site = {
                    "se": __class__.__name__,
                    "keyword": keyword,
                    "ad_site_url": ad_site_url,
                    "ad_site_domain": parsed_domain,
                    "ad_url": ele2[0].get_attribute('data-rw'),
                    "ad_text": ele1[0].text
                }
                self.driver.execute_script(
                    """
                    document.querySelector("div[aria-modal='true']").remove();
                    """
                )
                print(f"Suspected Ads: {ph_site['ad_site_url']}")
                self.take_screenshot(page[0], f'{keyword.replace(" ", "-")}_{parsed_domain}')
                ph_url = self.get_ph_site(ph_site['ad_url'])
                ph_site.update({"ph_url": ph_url})
                self.ph_site_list.append(ph_site)

    def search(self):
        for keyword in json.loads(self.settings["se_keywords"]):
            time.sleep(1)
            print(f"Searching on {__class__.__name__} for '{keyword}'")
            self.driver.get(f'https://www.google.com/search?q={keyword}')
            ads = self.wait_for_elements(self.driver, "//span[contains(text(),'Sponsor')]/..")
            for ad in ads:
                self.search_ad(ad, keyword)
        self.send_pushbullet()
