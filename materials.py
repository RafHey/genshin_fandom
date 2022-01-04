from os import mkdir
from bs4 import BeautifulSoup, element
from bs4.dammit import xml_encoding
from vars import MATERIALS_HEADINGS_ID
from base_fetcher import BaseFetcher

class Material(BaseFetcher):
    def __init__(self, client, link):
        self.link = link
        self.client = client
        super().__init__()
        self.fetch()
        
    
    def fetch(self):
        url = self.fetch_url(self.link.replace('/','',1))
        src = self.get_content(url)

        BSObj = BeautifulSoup(src, 'lxml')

        data_source_keys = self.data_source_keys(BSObj)
        self.main_info(BSObj, data_source_keys)
        for heading in MATERIALS_HEADINGS_ID:
            heading_ = heading.title()
            element = BSObj.find('span', {'id': heading_})
            if element is not None:
                element = element.parent
                try:
                    func = getattr(self, heading)
                except AttributeError:
                    pass
                else:
                    func(BSObj,element)

    def video_guides(self, BSObj, video_guide_heading):
        list_ = []
        element_ = video_guide_heading.find_next_sibling()
        while element_.name != 'h2':
            if element_.name == 'div':
                video = element_.find('div', {'class': 'embedvideowrap'})
                title = element_.find('div', {'class': 'thumbcaption'})
                title = element_.text.strip() if title is not None else ''
                if video is not None:
                    if video.find('iframe') is not None:
                        list_.append({
                            'link': video.find('iframe').attrs['src'],
                            'title': title
                        })
        self.__dict__['video_guides'] = list_

    def shop_availability(self, BSObj, shop_availablility_heading):

        element_ = shop_availablility_heading.find_next_sibling()
        while element_.name != 'table':
            element_ = element_.find_next_sibling()
        list_ = []
        keys_e = element_.find('tr')
        keys = [self.generate_key(e.text.strip()) for e in keys_e.find_all('th')]
        values_e = element_.find_all('tr')[1:]
        for values in values_e:
            vs = [e.text.strip().replace(',','',99) for e in values.find_all('td')]
            row_dict = dict(zip(keys,vs))
            list_.append(row_dict)
        self.__dict__['shop_availability'] = list_

    def gallery(self, BSObj, gallery_heading):
        element_ = gallery_heading.find_next_sibling()
        list_ = []
        while element_.name != 'h2':
            if element_.name == 'div':
                img = ''
                if 'class' in element_.attrs and element_.attrs['class'] == 'wikia-gallery-item':
                    img = self.find_image(element_)
                text_ = element_.find('div', {'class': 'lightbox-caption'})
                text_ = text_.text if text_ is not None else ''
                list_.append({
                    'img': img,
                    'title': text_
                })
        self.__dict__['gallery'] = list_

    def talent_leveling_usage(self, BSObj, talent_leveling_usage_heading):
        type_talent = ''
        element_ = talent_leveling_usage_heading.find_next_sibling()
        weapons_list = self.client.bows + self.client.catalysts + self.client.polearms + self.client.swords + self.client.claymores
        dict_ = {'weapons': weapons_list, 'characters': self.client.characters}
        while element_.name != 'h2':
            if element_.name == 'p':
                type_talent = element_.find('a').attrs['title'].lower()
            if element_.name == 'div':
                item = element_.find('div', {'class': 'card_caption'})
                if item is not None:
                    id_ = self.generate_key(item.find('a').attrs['title'])
                    navigatable = self.client.filter_navigatable(dict_[type_talent], id=id_)
                    if bool(navigatable):
                        navigatable = navigatable[0]
                    else:
                        navigatable = None
                    if f'talent_{type_talent}' in self.__dict__:
                        if navigatable is not None:
                            self.__dict__[f'talent_{type_talent}'].append(navigatable)
                    
                    else:
                        if navigatable is not None:
                            self.__dict__[f'talent_{type_talent}'] = [navigatable]
                        
            element_ = element_.find_next_sibling() 
      
    def craft_usage(self,BSObj, craft_usage_heading):
        bs = BSObj
        element_ = craft_usage_heading.find_next_sibling()
        table = None
        list_ = []
        while element_.name != 'h2':
            if element_.name == 'table':
                table = element_
            element_ = element_.find_next_sibling()
        if table is not None:
            keys = table.find('tr')
            rows = table.find_all('tr')[1:]
            keys_ = []
            values_ = []
            if keys is not None:
                keys_ = [self.generate_key(i.text.strip()) for i in keys.find_all('th')]
            for row in rows:
                columns = row.find_all('td')
                values_ = [e.text.strip() for e in columns]
                value_list = values_[-1].replace('\xa0','/n',99).split('/n')
                value_dict = {value_list[i]: value_list[i+1].replace('×','',99).replace(',','',99) for i in range(0, len(value_list), 2)}
                values_[-1] = value_dict
                list_.append( dict(zip(keys_, values_)))
        self.__dict__['craft_usage'] = list_

    def alchemy(self, BSObj, alchemy_heading):

        recipes = BSObj.find_all('div', {'class': 'new_genshin_recipe_container'})
        recipe_list = []
        for recipe in recipes:
            header = recipe.find('span', {'class': 'new_genshin_recipe_header_text'})
            header_text = ''
            if header is not None:
                header_text = header.text
            body = recipe.find('div', {'class': 'new_genshin_recipe_body'})
            items = []
            if body is not None:
                cards = body.find_all('div', {'class': 'card_with_caption'})
                for card in cards:
                    if 'new_genshin_recipe_body_yield' not in card.parent.attrs['class']:
                        item_name = card.find('div', {'class': 'card_image'})
                        if item_name is not None:
                            if item_name.find('a') is not None:
                                item_name = item_name.find('a').attrs['title']
                        item_amount = card.find('div', {'class': 'card_text'})
                        if item_amount is not None:
                            item_amount = item_amount.text.strip()
                        items.append({
                            'name': item_name,
                            'amount': item_amount
                        })
                    else:
                        item_name = card.find('div', {'class': 'card_image'})
                        if item_name is not None:
                            if item_name.find('a') is not None:
                                item_name = item_name.find('a').attrs['title']
                        item_amount = card.find('div', {'class': 'card_text'})
                        if item_amount is not None:
                            item_amount = item_amount.text.strip()
                        
                        recipe_list.append({
                            header_text : {
                                'items': items,
                                'yield' : {
                                    'name' : item_name,
                                    'amount': item_amount
                                }
                            }
                        })

        self.__dict__['recipes'] = recipe_list


    def data_source_keys(self, BSObj : BeautifulSoup):
        ds = BSObj.find_all(attrs={'data-source':True})
        return [d.attrs['data-source'] for d in ds]

    def main_info(self, BSObj: BeautifulSoup, keys: list):
        keys = keys
        omits = ['image', 'rarity']
        for key in keys:
            
            if key not in omits:
                data_source_class = BSObj.find(attrs={'data-source' : key})
                if data_source_class.find('h3') is not None:
                    text = data_source_class.text.replace(data_source_class.find('h3').text, '', 1).strip()
                    if key == 'type':
                        key = f'item_{key}'
                    self.__dict__[key] = text
        image =  BSObj.find(attrs={'data-source' : 'image'})
        rarity = BSObj.find(attrs={'data-source': 'rarity'})
        if rarity is not None:
            if rarity.find('img') is not None:
                rarity = int(rarity.find('img').attrs['alt'][0])
            else:
                rarity = 0
        else:
            rarity = 0
        self.__dict__['rarity'] = rarity
        self.__dict__['image'] = self.find_image(image)
        pass

    def ascension_usage(self,  BSObj, ascension_usage_heading):
        type_ascension = ''
        element_ = ascension_usage_heading.find_next_sibling()
        weapons_list = self.client.bows + self.client.catalysts + self.client.polearms + self.client.swords + self.client.claymores
        dict_ = {'weapons': weapons_list, 'characters': self.client.characters}
        while element_.name != 'h2':
            if element_.name == 'p':
                type_ascension = element_.find('a').attrs['title'].lower()
            if element_.name == 'div':
                item = element_.find('div', {'class': 'card_caption'})
                if item is not None:
                    id_ = self.generate_key(item.find('a').attrs['title'])
                    navigatable = self.client.filter_navigatable(dict_[type_ascension], id=id_)
                    if bool(navigatable):
                        navigatable = navigatable[0]
                    else:
                        navigatable = None
                    if f'ascension_{type_ascension}' in self.__dict__:
                        if navigatable is not None:
                            self.__dict__[f'ascension_{type_ascension}'].append(navigatable)
                    
                    else:
                        if navigatable is not None:
                            self.__dict__[f'ascension_{type_ascension}'] = [navigatable]
                        
            element_ = element_.find_next_sibling() 
      
        




    @property
    def full_details(self):
        dict_ = {}
        omits = ['session','link']
        for i in self.__dict__:
            if i not in omits:
                if 'source' in i:
                    if 'source' not in dict_:
                        dict_['source'] = [self.__dict__[i]]
                    else:
                        dict_['source'].append(self.__dict__[i])
                else:
                    dict_[i] = self.__dict__[i]
        return dict_



