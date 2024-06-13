import pandas as pd
import requests 

from datetime import datetime
from random import randint
from time import sleep

def current_dt():
    result = datetime.now().strftime("%m%d_%H:%M")
    return result

'''
City codes:
1 - Moscow
2 - Saint-Petersburg
'''

def get_list(keyworld, page=0, city_code=2):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyworld,
        "area": city_code,  
        "per_page": 100, 
        "page": page
    }

    headers = {
        "User-Agent": 
            "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",  
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        return data
    
    else: 
        print("Error: " + str(response.status_code))
    

def deconstruct(data):
    items = data['items']

    singular_values = ['name', 'has_test', 'response_letter_required', 
            'published_at', 'archived', 'alternate_url']
    partial_values =   {'type':'id', 'employer': 'trusted', 'schedule': 'id', 
            'experience': 'id', 'employment': 'id'}
    arrays = {'salary':['from', 'to', 'currency', 'gross'],
            'address':['raw', 'lat', 'lng'], 
            'snippet':['responsibility', 'requirement']}
    #exceptions = {'address'->'metro'->'station_name', 'professional_roles':'name'}

    result = []

    for item in items:
        extracted_values = {}

        for value in singular_values:
            extracted_values[value] = item[value]
        
        for key, value in partial_values.items():
            extracted_values[value] = item[key][value]
        
        for key, values in arrays.items():
            if item[key] is None:
                for value in values:
                    extracted_values[value] = None
                
            else:
                for value in values:
                    extracted_values[value] = item[key][value]

        if item['address'] is not None and item['address']['metro'] is not None:
            extracted_values['metro'] = item['address']['metro']['station_name']
        else:
            extracted_values['metro'] = None    
        
        extracted_values['role'] = item['professional_roles'][0]['name']
        
        result.append(extracted_values)

    return result

def get_page(keyword='python', page=0, delay=True, last_page=False):
    batch = get_list(keyword, page)
    data = deconstruct(batch)
    
    if delay:
        sleep(randint(5, 10))

    if last_page:
        return pd.DataFrame(data), batch['pages']

    return pd.DataFrame(data)


if __name__ == "__main__":
    df, last_page = get_page(last_page=True)
    current_page = 1

    while current_page != last_page + 1:
        print(f"Page {current_page} of {last_page}")
        df = pd.concat([df, get_page(page=current_page)])
        current_page += 1
        
    
    df.to_csv(f'{current_dt()}.csv')


    
