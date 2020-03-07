import requests
import json
import time

i=0
flag=0
API_KEY1 = 'uJ4YOf3-zwSN0dLgGaKvummX-Ik6LbPxDHMHfl8_rbXiHC6wwIYSPIIGq5i4chxBZ0UbT2_OgFGQCRLo_z7mBLRI1GydJG6uNtBDt8YPA13DuuACOEiOuOMmlFtbXnYx'
API_KEY2 = 'VldGz389ljqWXn0soyhWG6ijsHsskWkPohYjSe0_9ZgXseeERt1UX2uRTdLz3L5dOpfFqIxxjaNMvFOgQWS_02JZW9bUByY6o8K1BHGi2DwoAOycL73AyVDAVL9dXnYx'
while i<10:
    if(flag==0):
        API_KEY=API_KEY1
    else:
        API_KEY=API_KEY2
    ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
    HEADERS = {'Authorization': 'bearer %s' % API_KEY}

    PARAMETERS = {'term': 'Turkish restaurants',
                'limit': 50,
                'offset': 0+(i*50),
                'location': 'Manhattan'}

    response = requests.get(url = ENDPOINT,
                            params = PARAMETERS,
                            headers = HEADERS)

    business_data = response.json()

    for x in business_data['businesses']:
        print(x['name'])

    name= "{}{}.json"

    with open(name.format(PARAMETERS['term'],i), 'w', encoding='utf-8') as f:
        json.dump(business_data['businesses'], f, ensure_ascii=False, indent=4)
    i=i+1
    if flag==0:
        flag=1
    else:
        flag=0