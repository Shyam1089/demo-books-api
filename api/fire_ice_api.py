# Adapter for the fire and ice api
import requests
import json

from flask_api import status

URL = "https://www.anapioficeandfire.com/api"
JSON_TYPE_HEADERS = {'Content-Type': 'application/json'}

def get_books(query_params={}):
    url = f'{URL}/books'
    response: Response = requests.get(url, headers=JSON_TYPE_HEADERS, params=query_params)
    return response.status_code, json.loads(response.content.decode('utf-8'))