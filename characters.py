
from base_fetcher import BaseFetcher
from vars import *
from bs4 import BeautifulSoup

class Character(BaseFetcher):
    def __init__(self, client, link):
        self.client = client
        self.link = link
        super().__init__()
        self.fetch()
        

    def fetch(self):
        url = self.fetch_url(self.link)
        print(url)
        src = self.get_content(url)
        BSObj = BeautifulSoup(src, 'lxml')
        data_sources = [{'td': 'rarity'},{'td': 'element'}, {'h2': 'secondary_title'}, {'h2': 'name'}, {'div': 'realname'}, {'div': 'sex'} , {'div': 'birthday'}, {'div' :'constellation'} , {'div':'region' } , {'div': 'affiliation'}, {'div': 'dish'}, {'div': 'obtain'}, {'div': 'releaseDate'}, {'div': 'ancestry'}, {'div': 'parents'}, {'div': 'siblings'}, {'div': 'voiceEN'}, {'div': 'voiceJP'}, {'div': 'voiceKR'}, {'div': 'voiceCN'}]
        omit_data_sources = ['releaseDate', 'sex', 'voiceEN', 'voiceCN', 'voiceKR', 'voiceJP','birthday']
        for data_source in data_sources:
            data_source_tag = list(data_source.keys())[0]
            data_source_class = data_source[data_source_tag]

            data_source_element = BSObj.find(data_source_tag, {'data-source': data_source_class})

            if data_source_element is not None:
                if data_source_class == 'rarity':
                    self.__dict__[data_source_class] = int(data_source_element.find('img').attrs['alt'][0])
                else:

                    if data_source_element.find('h3') is not None:
                        value = data_source_element.text.replace(data_source_element.find('h3').text.strip(), '' , 99).strip()
                        if data_source_element.find('a') is not None and data_source_class not in omit_data_sources:
                            value = [a.text.strip() for a in data_source_element.find_all('a')]
                        if isinstance(value, list):
                            if data_source_class in value[0].lower():
                                value = value [1] if len(value[1:]) == 1 else value[1:] 
                            value = value[0] if len(value) == 1 else value                   
                        self.__dict__[data_source_class] = value
                    else:
                        self.__dict__[data_source_class] = data_source_element.text.strip().split('/n') if len(data_source_element.text.strip().split('\n')) > 1 else data_source_element.text.strip()

        '''

        Talents scraping

        '''

        talent_table = BSObj.find('table', {'class': 'talent_table'})
        if talent_table is not None:
            rows = talent_table.find_all('tr')
            for row in rows:

                #check if it contains talent basic info
                columns = row.find_all('td')
                main_check = len(columns) == 3

                if main_check:
                    name = columns[1].text.strip()
                    icon = self.find_image(columns[0])
                    type = columns[2].text.strip()
                    link = columns[1].find('a').attrs['href']
                    item_dict = {
                        'name': name,
                        'icon': icon,
                        'atk_type': type,
                        'link': link,
                        'type': 'talents' 
                    }
                    self.add_navigatable(self.client,self.__dict__, 'talents', item_dict, True)

        constellation_table = BSObj.find('span', {'id': 'Constellation'})
        if constellation_table is not None:
            constellation_table = constellation_table.parent.find_next_sibling()
        
        rows = constellation_table.find_all('tr')
        for row in rows:

            columns = row.find_all('td')

            main_check = len(columns) == 4

            if main_check:

                level = int(columns[0].text.strip())
                icon = self.find_image(columns[1])
                name = columns[2].text.strip()
                link = columns[2].find('a').attrs['href'][columns[2].find('a').attrs['href'].find('wiki/')+len('wiki/'):]
                effect = columns[3].text.strip()

                item_dict = {
                    'level': level,
                    'icon': icon,
                    'name': name,
                    'link' : link,
                    'effect' : effect,
                    'type': 'constellations'
                }
                self.add_navigatable(self.client, self.__dict__, 'constellations', item_dict, True)
        tu_table = BSObj.find('span', {'id': 'Talent_Upgrade'})
        if tu_table is not None:
            tu_table = tu_table.parent.find_next_sibling()
            self.talent_upgrade(tu_table)

    @property
    def constellation_names(self):
        if bool(self.constellations):
            return [conste.__dict__['name'] for conste in self.constellations]

    @property
    def talent_names(self):
        if bool(self.talents):
            return [talent.__dict__['name'] for talent in self.talents]

    def constellation_detail(self, constellation_name: str):
        for conste in self.constellations:
            if constellation_name.lower() in conste.__dict__['name'].lower():
                return {
                    'name': conste.__dict__['name'],
                    'level' : conste.__dict__['level'],
                    'effect' : conste.__dict__['effect'],
                    'icon' : conste.__dict__['icon']
                }
    
    def __repr__(self) -> str:
        return self.name

    def talent_upgrade(self, table_element):

        keys_element = table_element.find('tr')
        keys = {}
        level_up_key = ''
        for count,key in enumerate(keys_element.find_all('th')):
            if count <= 3:
                keys[str(count)] = self.generate_key(key.text.replace('[Subtotal]','',99).strip())
            else:
                level_up_key = self.generate_key(key.text.replace('[Subtotal]','',99).strip())
        keys['4'] = level_up_key
        keys['5'] = level_up_key
        keys['6'] = level_up_key

        rows_elements = table_element.find_all('tr')[1:]
        rows_elements_fixed = []
        last_column = []
        check = lambda x : len(x) == 7

        for row_element in rows_elements:
            columns = row_element.find_all('td')

            if check(columns):
                rows_elements_fixed.append(columns)
                last_column = columns
            else:
                if len(columns) >= 5:
                    if len(last_column) > len(columns):
                        for c in list(range(len(columns)+1, len(last_column),1)):
                            columns.insert(c,last_column[c])
                    if not check(last_column):
                        for c in list(range(len(columns), 8, 1)):
                            columns.insert(c,None)
                    rows_elements_fixed.append(columns)
                else:
                    if len(last_column) > len(columns):
                        columns.insert(1, last_column[1])
                        for c in list(range(len(columns)+1, len(last_column),1)):
                                columns.insert(c,last_column[c])
                    if not check(last_column):
                        for c in list(range(len(columns), 8, 1)):
                            columns.insert(c,None)
                    rows_elements_fixed.append(columns)
        list_ = []           
        for row in rows_elements_fixed:
            temp_dict_ = {}
            for c,column in enumerate(row):
                key = keys[str(c)]
                if column.find('div',{'class':'card_container'}) is not None:
                    title, image, amount = self.card_element(column.find('div', {'class':'card_container'}))
                    temp_dict_[key] = {
                        'title': title,
                        'image': image,
                        'amount' : amount
                    }
                else:
                    temp_dict_[key] = column.text.strip()
            list_.append(temp_dict_)
        self.__dict__['talent_upgrade'] = list_










        




    @property
    def full_details(self):
        dict_ = {}
        omits = ['link','session','constellations','talents']
        for i in self.__dict__:
            if i not in omits:
                dict_[i] = self.__dict__[i]
        dict_['constellations'] = [conste.details for conste in self.constellations]
        dict_['talents'] = [talent.details for talent in self.talents]
        return dict_
