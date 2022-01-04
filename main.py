from typing import Dict, List
from requests.sessions import Session
from bs4 import BeautifulSoup, element
from vars import *
from navigate import Navigatable
from json import dump, load
from os import closerange, getcwd
from os.path import exists
from datetime import datetime, timedelta
from time import sleep


#
#
#   TODO: cached navigatables
#         seperate_functions for scraping materials, items, weapons, artifacts
#

class GenshinFandomClient:
    def __init__(self):
        self.session = Session()
        self.data = {}
        self.navigatables = []
        self.cached_data()

    def get_content(self, url: str):
        if url.startswith('http'):
            status_ = self.session.get(url)
            if status_.status_code != 404:
                return status_.content

    def generate_key(self, key : str):
        seperators = ['-',':','.',')','(','!',';',"'",'`','#','%']
        for seperator in seperators:
            key = key.replace(seperator,'_',99)
        key = key.replace('%27','',99).replace(' ','_',99).replace('_s_','s_',99).lower()
        return key[:-1] if key[-1] == '_' else key
    

    def prettify(self, id: str):

        return id.replace('_',' ',99).title()

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
    
    


    def fetch_url(self, extend: str):
            return BASE_URL.format(extend=extend)


    def fetch_character_list(self) -> List:
        url = self.fetch_url(CHARACTERS_LIST)
        data = []
        src = self.get_content(url)
        bs = BeautifulSoup(src, 'lxml')
        link_column = 1
        tables = bs.find_all('table')

        key = CHARACTERS_LIST.split('/')[0]
        for table in tables[:2]:
            rows = table.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 6:
                    link = columns[link_column].find('a')
                    if link is not None:
                        id = link.attrs['href'].split('/')[-1]
                        if columns[2].find('img') is not None: 
                            rarity = int(columns[2].find('img').attrs['alt'][0])
                        else:
                            rarity = 0
                        element = columns[3].text.strip()
                        weapon = columns[4].text.strip()
                        nation = columns[5].text.strip()
                        link = link.attrs['href'][link.attrs['href'].find('wiki/')+len('wiki/'):]
                        item =  {
                        'link' : link,
                        'id' : self.generate_key(id),
                        'name': self.prettify(self.generate_key(id)),
                        'type': key.lower(),
                        'element' : element,
                        'nation': nation,
                        'rarity' : rarity,
                        'weapon' : weapon
                    }
                        if item not in data:
                            data.append(item)

        return data

    def fetch_artifact_list(self) -> List:
     
        url = self.fetch_url(ARTIFACTS_LIST)
        data = []
        src = self.get_content(url)
        bs = BeautifulSoup(src, 'lxml')
        link_column = 0
        tables = bs.find_all('table')

        key = 'artifacts'
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:
                columns = row.find_all('td')
                if len(columns) >= 4:
                    link = columns[link_column].find('a')
                    if link is not None:
                        id = link.attrs['href'].split('/')[-1]
                        rarity = []
                        if columns[2].find('img') is not None: 
                            temp_rarity = columns[1].text.strip().replace('★','',1).split('-')
                            if len(temp_rarity) == 2:
                                rarity = list(range(int(temp_rarity[0]),int(temp_rarity[1])+1))
                            else:

                                rarity = [int(temp_rarity[0])]
                        else:
                            rarity = [0]
                        pieces = list(range(1,len(columns[2].find_all('span',{'class': 'item_image'}))+1))
                        link = link.attrs['href'][link.attrs['href'].find('wiki/')+len('wiki/'):]
                        item =  {
                        'link' : link,
                        'id' : self.generate_key(id),
                        'name': self.prettify(id),
                        'type': key.lower(),
                        'rarity': rarity,
                        'pieces' : pieces
                        
                    }
                        if item not in data:
                            data.append(item)

        return data

    def fetch_weapon_list(self, weapon_type: str) -> List:
        weapons = dict(zip(WEAPON_TYPES, [BOWS_LIST, CLAYMORES_LIST, POLEARMS_LIST, CATALYST_LIST, SWORDS_LIST]))
        type_ = weapons[weapon_type]
        url = self.fetch_url(f'{type_}')
        data = []
        src = self.get_content(url)
        bs = BeautifulSoup(src, 'lxml')
        link_column = 1
        tables = [table_ for table_ in bs.find_all('p') if 'weapons match' in table_.text.lower()]
        table = None
        if bool(tables):
            table = tables[0].find_next_sibling()
        key = 'weapons'
        if table is not None:
            rows = table.find_all('tr')[1:]
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 6:
                    link = columns[link_column].find('a')
                    if link is not None:
                        id = link.attrs['href'].split('/')[-1]
                        if columns[2].find('img') is not None: 
                            rarity = int(columns[2].find('img').attrs['alt'][0])
                        else:
                            rarity = 0
                        icon = self.find_image(columns[0])
                        
                        link = link.attrs['href'][link.attrs['href'].find('wiki/')+len('wiki/'):]
                        item =  {
                        'link' : link,
                        'id' : self.generate_key(id),
                        'name': self.prettify(id),
                        'type': key.lower(),
                        'icon': icon,
                        'rarity' : rarity,
                        'weapon_type': weapon_type
                        
                    }
                        if item not in data:
                            data.append(item)

        return data

    def fetch_materials_list(self) -> List:

        url = self.fetch_url(MATERIALS_MAIN)

        src = self.get_content(url)
        BSOBj = BeautifulSoup(src, 'lxml')
        data = []
        ids = ['Common_Ascension_Materials', 'Character_EXP_Materials', 'Character_Ascension_Materials', 'Character_Talent_Materials', 'Weapon_Enhancement_Materials', 'Weapon_Ascension_Materials', 'Weapon_Refinement_Materials', 'Artifact_Materials', 'Local_Specialties', 'Bait', 'Fish', 'Cooking_Ingredients', 'Forging_Materials', 'Uncategorized_Materials', 'Furnishing_Materials', 'Gardening_Materials']
        for h_id in ids:
            span_ = BSOBj.find('span', {'id' : h_id})
            type_ = None
            table_ = None
            if span_ is not None:
                type_ = self.generate_key(span_.attrs['id'])
            table_ = span_.parent.find_next_siblings('div', {'class': 'columntemplate'})[0]
            if table_ is not None and type_ is not None:
                items_lists = table_.find_all('span', {'class': 'item_image'})
                for item in items_lists:
                    if item.find('a') is not None:
                        title = item.find('a').attrs['title']
                        link = item.find('a').attrs['href'][item.find('a').attrs['href'].find('wiki/')+len('wiki'):]
                        icon = self.find_image(item)
                        item_dict = {
                            'type': type_,
                            'id' : self.generate_key(title),
                            'name': title,
                            'icon': icon,
                            'link': link
                        }
                        if item_dict not in data:
                            data.append(item_dict)
        return data

    def filter_navigatable(self, list_ : List[Navigatable], **kwargs) -> List[Navigatable]:
        result = []
        
        kwargs = dict(kwargs)
        for item in list_:
            add = False
            for kwarg in kwargs:
                if kwarg in item.full_details:
                    if kwargs[kwarg] == item.full_details[kwarg]:
                        add = True                        
            if add == True and item not in result:
                result.append(item)
        return result

    def cached_data(self):
        fetch_limit = 86400
        fetch = True
        elapsed = 0
        if exists('data.json'):

            with open('data.json', 'r') as f:

                self.data = load(f)

            fetch_datetime = datetime.strptime(self.data['fetchtime'], '%c')
            if  fetch_datetime < datetime.now():
                elapsed = (datetime.now()-fetch_datetime).seconds
                if elapsed > fetch_limit:

                    fetch = True
                
                else:
                    
                    fetch = False
            
            else:

                fetch = False

        else:

            fetch = True

        if fetch == False:

            print('[GenshinFandomClient]', 'cached data', 'loaded',' | 1 day has not passed since last data update!', 'elapsed seconds', elapsed)
        if fetch == True:

            characters = self.fetch_character_list()

            self.data['characters'] = characters

            sleep(2)

            for weapon in WEAPON_TYPES:

                list_ = self.fetch_weapon_list(weapon)

                self.data[weapon] = list_

                sleep(2)
            
            list_ = self.fetch_artifact_list()
            self.data['artifacts'] = list_
            sleep(2)

            list_ = self.fetch_materials_list()
            self.data['materials'] = list_

            self.data['fetchtime'] = datetime.now().strftime('%c')

            with open('data.json', 'w') as f:
                dump(self.data, f, indent=1)

            print('[GenshinFandomClient]','cached data', 'updated!')
        
        self.create_navigatables()
        
    def create_navigatables(self):

        if bool(self.data): #if data is not empty

            for type_ in self.data:

                for item in self.data[type_]:

                    if type(self.data[type_]) == str:

                        self.__dict__[type_] = self.data[type_]
                    
                    else:


                        if type_ in self.__dict__:

                            self.__dict__[type_].append( Navigatable(self, {**item, **{'value': True} }))
                        
                        else:
                            self.__dict__[type_]  = [Navigatable(self, {**item, **{'value': True}})]
            


    

    def fetch_list(self, page) -> List[Dict]:
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


    @property
    def items(self):        
        items_ = ['bows','characters', 'catalysts', 'swords', 'polearms', 'materials', 'claymores', 'artifacts']
        keys = list(self.__dict__.keys())
        return [i for i in items_ if i in keys]


client = GenshinFandomClient()
test_material = client.characters[0].navigate()

print(test_material)


