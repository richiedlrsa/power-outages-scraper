import re
from power_outages_api.electric_providers import ElectricProvider
from datetime import date, datetime
import locale

class Edesur(ElectricProvider):
    time_pattern = r'\d{1,2}:\d{2} [aApP]\.?\s?[mM]\.?'
    url = 'https://www.edesur.com.do/enlaces-empresa/mantenimientos-programados/'
    def __init__(self):
        self.soup = ElectricProvider.get_soup(self.url)
        super().__init__(Edesur.url)
        
    def _get_day_ids(self) -> list:
        """
        Gets the ids of the tags contaning the scheduled maintenance for each day
        Returns a list of ids
        """
        nav_list = self.soup.find('ul', class_ = 'nav nav-pills nav-fill')
        return [tag['id'].replace('-tab', '') for tag in nav_list.find_all('button')]
    
    def _parse_city(self, tag) -> list:
        """
        Obtains the different timeblocks and associated sectors for each city
        Returns a list of dictonaries mapping time: timeblock, sectors: list of sectors
        """
        times = tag.find_all('h5', class_ = 'title-zona')
        sectors = tag.find_all(lambda tag: tag.name == 'p' and tag.text.strip(), class_ = False)
        maintenance = []
        for time, sectors in zip(times, sectors):
            time = re.findall(Edesur.time_pattern, time.text)
            if len(time) < 2:
                time = 'Time data not available.' 
            else:
                time = f'{time[0]} - {time[1]}' 
            maintenance.append({'time': time, 'sectors': sectors.text.split(',')})
        
        return maintenance
        
    def _organize_data(self) -> list:
        """
        Scrapes and organizes the data for the scheduled maintenance for each day
        Returns a list of dictionaries
        """
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        data = []
        for item in self._get_day_ids():
            day = self.soup.find('button', id = item + '-tab')
            if not day:
                continue
            day = day.text.strip('\n').replace('\n', ' ')
            province_tags = self.soup.select(f'#{item} .accordion-item')
            for tag in province_tags:
                province = tag.find('h4', class_ = 'mb-0')
                if not province:
                    continue
                try:
                    formatted_date = str(datetime.strptime(day, '%A %d de %B, %Y').date())
                except ValueError:
                    formatted_date = 'Date not available.'
                province = province.text.strip()
                data.append({
                    'company': 'Edesur',
                    'week_number': f'{date.today().isocalendar()[1]}',
                    'day': formatted_date,
                    'province': province,
                    'maintenance': self._parse_city(tag)
                }) 
                
        return data