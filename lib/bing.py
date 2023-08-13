import time
import json

from .se import AdsMonitor


class Bing(AdsMonitor):

    def __init__(self, settings: tuple):
        AdsMonitor.__init__(self, settings)

    def search_ad(self, ad: str, keyword: str):
        page = self.wait_for_elements(self.driver, "body")
        ad_infos = self.wait_for_elements(ad, "h2 a")
        site_url = self.wait_for_elements(ad, ".b_caption  a")
        if site_url and ad_infos and site_url[0].text != '':
            parsed_domain = AdsMonitor.get_domain_from_url(site_url[0].text)
            is_suspect = True if parsed_domain not in json.loads(self.settings["accepted_domains"]) else False
            if is_suspect:
                ph_site = {
                    "se": __class__.__name__,
                    "keyword": keyword,
                    "ad_site_url_text": site_url[0].text,
                    "ad_domain": parsed_domain,
                    "ad_link": ad_infos[0].get_attribute('href'),
                    "ad_text": ad_infos[0].text,
                }
                self.driver.execute_script(
                    """
                    var l = document.getElementsByClassName("bnp_cookie_banner")[0];
                    if(l) {l.parentNode.removeChild(l);}
                    """
                )
                print(f"Suspected Ads: {ph_site['ad_site_url_text']}")
                self.screenshot(page[0], f'{keyword.replace(" ", "-")}_{parsed_domain}')
                ph_url = self.get_ph_site(ph_site['ad_link'])
                ph_site.update({"ph_url": ph_url})
                self.ph_site_list.append(ph_site)

    def search(self):
        for keyword in json.loads(self.settings["se_keywords"]):
            time.sleep(1)
            print(f"Searching on {__class__.__name__} for '{keyword}'")
            self.driver.get('https://www.bing.com/search?q=' + keyword)
            ads = self.wait_for_elements(self.driver, 'li.b_adTop ul li .sb_add')
            for ad in ads:
                self.search_ad(ad, keyword)
        if self.pb and self.ph_site_list:
            self.pb.push_note("Suspect Ads detected", "\n".join([f"{k}: {v}" for x in  self.ph_site_list for k, v in x.items()]))
        self.driver.close()
