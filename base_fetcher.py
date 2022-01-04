from requests.sessions import Session
from bs4 import BeautifulSoup
from vars import *
from navigate import Navigatable
class BaseFetcher:
    def __init__(self):
        self.session = Session()

    def get_content(self, url: str):
        if url.startswith('http'):
            status_ = self.session.get(url)
            if status_.status_code != 404:
                return status_.content

    def generate_key(self, key : str):
        seperators = ['-',':','.',')','(','!',';',"'",'`','#','%','%27']
        for seperator in seperators:
            key = key.replace(seperator,'_',99)
        key = key.replace(' ','_',99).replace('_s_','s_',99).lower()
        print(key)
        return key[:-1] if key[-1] == '_' else key
    
    def find_image(self, division):
        if division.name != 'img':
            division = division.find('img')
        
        if division is not None:
            if 'data-src' in division.attrs:
                if division.attrs['data-src'].startswith('http'):
                    return division.attrs['data-src'][:division.attrs['data-src'].find('/revision')]
            if 'src' in division.attrs:
                if division.attrs['src'].startswith('http'):
                    return division.attrs['src'][:division.attrs['src'].find('/revision')]

        return IMAGENOTFOUND
    
    def add_navigatable(self, client, data_dict: dict , main_key: str,  item_dict: dict,  value: bool = False):
    
        if main_key in data_dict:
            data_dict[main_key].append( Navigatable(client, { **item_dict, 
                                                **{'value': value
            }}
            )) 
        else:
            data_dict[main_key] = [Navigatable(client,{ **item_dict, 
                                                **{'value': value
            }})]

    def fetch_url(self, extend: str):
            return BASE_URL.format(extend=extend)

    def type_check(self, type_, item_name):
        if type_ == 'characters':
            list_ = self.fetch_list(CHARACTERS_LIST)
        if type_ == 'weapons':
            list_ = self.fetch_list(BOWS_LIST) + self.fetch_list(CLAYMORES_LIST) + self.fetch_list()
        list_ = self.fetch_list(type_)
        for item in list_:
            string = item.replace('_', ' ',99).replace('%27B', ' ', 99).lower()
            if item_name.lower() in string:
                return True
    
    def all_navigatables(self):

        navigatables = []
        for i in self.__dict__:
            if isinstance(self.__dict__[i], Navigatable):
                navigatables.append(self.__dict__[i])
            if isinstance(self.__dict__[i], list):
                for item in self.__dict__[i]:
                    if isinstance(item, Navigatable):
                        navigatables.append(item)
        return navigatables

    def card_element(self, card_container):
        image = IMAGENOTFOUND
        amount = ''
        title = ''
        image_element = card_container.find('div', {'class':'card_image'})
        if image_element is not None:
            if image_element.find('a') is not None:
                title = image_element.find('a').attrs['title']
            image = self.find_image(image_element)
        amount_element = card_container.find('div', {'class': 'card_text'})
        if amount_element is not None:
            amount = amount_element.text.replace(',','',9).strip()
        if title == amount == '':
            return None, None, None
        return title, image, amount


    def fetch_list(self, page):
        url = self.fetch_url(page)
        data = {}
        src = self.get_content(url)
        bs = BeautifulSoup(src, 'lxml')
        link_column = 0 if page == ARTIFACTS_LIST else 1
        tables = bs.find_all('table')

        key = page.split('/')[0]
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 2:
                    link = columns[link_column].find('a')
                    if link is not None:
                        id = link.attrs['href'].split('/')[-1]
                        link = link.attrs['href'][link.attrs['href'].find('wiki/')+len('wiki/'):]
                        if key in data:
                            data[key].append ( {
                        'link' : link,
                        'id' : self.generate_key(id),
                        'type': key.lower()
                    })
                        else:
                            data[key] = [{
                                'link' : link,
                        'id' : self.generate_key(id),
                        'type': key.lower()
                            }]

        return data[key]

    

