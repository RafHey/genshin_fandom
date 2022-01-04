from typing import *

from vars import BASE_URL, MATERIALS_TYPES, SCRAPERS
from importlib import import_module
class Navigatable:
    def __init__(self, client, navigate_dict: dict):
        for i in navigate_dict:
            self.__dict__[i] = navigate_dict[i]
        self.client = client
        self.scraper = None
        self.set_scraper()

    def fetch_url(self, extend:str) -> str:
        return BASE_URL.format(extend=extend)

    def set_scraper(self):  
        type_ = self.type      
        module = SCRAPERS.get(type_, None)
        if self.type in MATERIALS_TYPES:
            module = SCRAPERS.get('materials')
            type_ = 'materials'
        if module is not None:
            scraper = getattr(import_module(type_), module)
            self.scraper = scraper

    
    def navigate(self, navigatable_dict: dict = None):
        if navigatable_dict is None:
            check = self.__dict__
        else:
            check = navigatable_dict
        if check.get('value', False) == True:
                return self.scraper(self.client, self.link)

    @property
    def details(self):
        dict_ = {}
        omits = ['scraper','id','link','type','value','client']
        for i in self.__dict__:
            if i not in omits:
                dict_[i] = self.__dict__[i]
        return dict_

    @property
    def full_details(self):
        return self.__dict__

