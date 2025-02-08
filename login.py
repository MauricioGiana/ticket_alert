import requests
from bs4 import BeautifulSoup
import constants

def get_token():
    response = requests.post(constants.LOGIN_URL, data=constants.LOGIN_DATA)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find('input', {'id': 'token'})
    
        if token_input:
            token = token_input.get('value')
            return token
        else:
            raise Exception("get_token: Token input not found")
    else:
        print(f'Error: {response.status_code}')
        raise Exception(f'get_token: Error: {response.status_code}')