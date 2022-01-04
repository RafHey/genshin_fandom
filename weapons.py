from base_fetcher import BaseFetcher

class Weapon(BaseFetcher):
    def __init__(self,client, link):
        self.client = client
        self.link = link