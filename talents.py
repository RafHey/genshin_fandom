from base_fetcher import BaseFetcher
from vars import *
from bs4 import BeautifulSoup

class Talent(BaseFetcher):
    def __init__(self,client,  link):
        self.client = client
        self.link = link
        super().__init__()
        self.fetch()
        

    def fetch(self):

        url = self.fetch_url(self.link)

        src = self.get_content(url)

        BSObj = BeautifulSoup(src, 'lxml')

        data_sources = [{'div': 'type'}, {'div': 'info'}, {'div': 'character'}]


        for data_source in data_sources:
            data_source_tag = list(data_source.keys())[0]
            data_source_class = data_source[data_source_tag]

            data_source_element = BSObj.find(data_source_tag, {'data-source': data_source_class})

            if data_source_element is not None:
                if data_source_element.find('h3') is not None:
                    self.__dict__[data_source_class] = data_source_element.text.replace(data_source_element.find('h3').text, '', 1).strip()
            
        '''

        Talent Notes

        '''

        note_heading = [h for h in BSObj.find_all('h2') if 'Notes' in h.text]

        note_heading = note_heading[0] if len(note_heading) >= 1 else None
    	
        notes = ''
        if note_heading is not None:
            notes_list = note_heading.find_next_sibling()
            notes = ''
            if notes_list is not None and notes_list.name == 'ul':
                notes = '\n'.join([note.text.strip() for note in notes_list.find_all('li')])
            
        self.__dict__['notes'] = notes

        '''
        ATK Preview Images

        '''

        images = BSObj.find_all('div', {'class': 'ogv-gallery-item'})

        check = len(images) >= 1
        self.__dict__['preview'] = []
        if check:
            for image in images:
                image_element = image.find('figure', {'class' : 'thumb'})
                text = image_element.find('figcaption').text if image_element.find('figcaption') is not None else ''
                self.__dict__['preview'].append({
                    'name': text,
                    'url': self.find_image(image_element)
                })
        
        '''

        Attribute scaling 
        '''

        keys = []
        levels = []
        attribute_dict = {}
        attribute_table = BSObj.find('span', {'id': 'Attribute_Scaling'})
        if attribute_table is not None:
            attribute_table = attribute_table.parent.find_next_sibling()
            rows = attribute_table.find_all('tr')
            
            levels = list(range(1, len(rows[0].find_all('th')) + 1, 1))
            fixed_rows = [row for row in rows if len(row.find_all('td')) != 0]
            for row in fixed_rows:
                keys.append(self.generate_key(row.find('th').text.strip()))
            for row in fixed_rows:
                row_values = []
                values = row.find_all('td')
                row_values = [val.text for val in values]
                if len(row_values) < levels[-1]:
                    row_values += [row_values[-1]] * (levels[-1] - len(row_values))
                
                row_mapped_values = dict(zip(levels,row_values))

                attribute_dict[keys[fixed_rows.index(row)]] = row_mapped_values
        
        self.__dict__['attributes'] = attribute_dict
        '''
        Talent Levelling
        '''

        ascension_table = BSObj.find('span', {'id' : 'Talent_Leveling'})
        ascension_dict = {}
        if ascension_table is not None:
            ascension_table = ascension_table.parent.find_next_sibling()

            rows = ascension_table.find_all('tr')
            required_last = 0
            for row in rows:

                columns = row.find_all('td')

                check = len(columns) >= 2
                if check:
                    level = int(columns[0].text.split('→')[1])
                    print(columns[1].text)
                    if '✦' in columns[1].text:
                        required = int(columns[1].text.replace('✦','',1))
                        required_last = required
                    else:
                        required = required_last
                    materials = []
                    materials_columns = row.find_all('div', {'class': 'card_image'})
                    for material in materials_columns:
                        if material.parent is not None:
                            title = material.find('a').attrs['title'] if material.find('a') is not None else ''
                            value = material.parent.find('div', {'class': 'card_text'}).text.strip()
                        
                            materials.append( {
                                'title': title,
                                'value' : int(value.split('.')[0].replace(',','',1000))
                            })
                    
                    ascension_dict[level] = {
                        'required_ascension' : required,
                        'materials': materials
                    }
        
        self.__dict__['ascension'] = ascension_dict

    @property
    def full_details(self):
        dict_ = {}
        omits = ['link','session']
        for i in self.__dict__:
            if i not in omits:
                dict_[i] = self.__dict__[i]
        return dict_
    





