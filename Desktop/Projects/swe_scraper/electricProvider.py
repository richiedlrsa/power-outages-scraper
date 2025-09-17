import requests
from bs4 import BeautifulSoup

class electricProvider:
    def __init__(self, url):
        self.url = url
        self.data = self._organize_data()
        
    @staticmethod
    def get_soup(url, headers = None):
        '''
        url: a string representation of the url we want to open
        headers (optional): metadata pertaining to the request
        Initiates the get request
        Returns a soup objects created from the response
        '''
        try:
            if headers:
                response = requests.get(url, headers = headers)
            else:
                response = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise Exception(f'Error fetching website: {e}')
        
        return BeautifulSoup(response.text, 'lxml')
    
    def _organize_data(self):
        pass
        