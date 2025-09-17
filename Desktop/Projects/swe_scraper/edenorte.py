import requests, locale, pandas as pd, io
from datetime import date, timedelta
from electricProvider import electricProvider

class edenorte(electricProvider):
    url = 'https://edenorte.com.do/category/programa-de-mantenimiento-de-redes/'
    def __init__(self):
        self.columns = ['province', 'day', 'time', 'sectors', '']
        super().__init__(edenorte.url)
        
    @staticmethod
    def get_monday() -> date:
        '''
        Calculates the start of the current week
        Returns a date object
        '''
        # sets the language of the date class to spanish
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        today = date.today()
        return (today - timedelta(days = today.weekday()))
    
    def _get_link(self) -> str:
        '''
        Grabs the link for the maintenance data related to the current week
        Returns a string representation of the link
        '''
        monday = self.get_monday()
        soup = self.get_soup(self.url)
        link_tag = soup.find(lambda tag: tag.name == 'a' and 
                              monday.strftime('%d') in tag.text and
                              monday.strftime('%B') in tag.text
                              )
        
        try:
            return link_tag['href']
        except KeyError:
            raise Exception('Error fetching link. Website structure may have changed.')
        
    def _get_file(self):
        '''
        Grabs the url for the download file and initiates the get request to download the file
        Returns the content of the file in binary
        '''
        monday = self.get_monday()
        soup = self.get_soup(self._get_link())
        divs = soup.find_all('div', class_ = 'w3eden')
        
        for div in divs:
            download_link_div = div.find(lambda tag: tag.name == 'a' and 
                                monday.strftime('%d') in tag.text and
                                monday.strftime('%B') in tag.text and 
                                ('excel' in tag.text or 
                                'EXCEL' in tag.text or
                                'Excel' in tag.text)
                                )
            
            if download_link_div:
                download_link_tag = div.find(lambda tag: tag.name == 'a' and 
                                tag.text.lower() == 'descargar'
                                )
        
            try:
                return requests.get(download_link_tag['data-downloadurl']).content
            except KeyError:
                raise Exception('Error downloading file. Website structure may have changed.')
        
    def _prepare_data(self):
        '''
        Opens a file-like object in memory
        Returns a pandas dataframe object created from the "file"
        '''
        excel_file = io.BytesIO(self._get_file())
        df = pd.read_excel(excel_file)
        df.columns = self.columns
        return df
    
    def _organize_data(self) -> list:
        '''
        Extracts and parses the data from the data frame object
        Returns a list of dictionaries
        '''
        data = []
        df = self._prepare_data()
        
        for day in df.day.unique():
            for province in df.province.unique():
                filtered_data = df[(df.day == day) & (df.province == province)]
                if filtered_data.empty:
                    continue
                maintenance = []
                for _, row in filtered_data.iterrows():
                    maintenance.append({'time': row.time, 'sectors': row.sectors.split(',')})
                
                # if the date is returned as an Excel serial number, convert it to a date time object and format it.
                if isinstance(row.day, int):
                    # an Excel date serial number represents n days from 1899-12-30. Adding those days gives the current date.
                    formatted_day = (date.fromisoformat('1899-12-30') + timedelta(days = day)).strftime('%A %d de %B')
                else:
                    formatted_day = day.strftime('%A %d de %B')
                    
                data.append({
                    'day': f"{formatted_day}, {date.today().year}",
                    'province': province,
                    'maintenance': maintenance
                }) 
                
        return data
            
def get_edenorte_data():
    edenorte_inst = edenorte()
    return edenorte_inst

if __name__ == '__main__':
    edenorte = get_edenorte_data()
    print(edenorte.data)