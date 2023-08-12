from .se import AdsMonitor


class Google(AdsMonitor):

    def __init__(self, settings: tuple):
        AdsMonitor.__init__(self, settings)

    def search_ad(self, ad: str, keyword: str):
        pass

    def search(self):
        pass
