import json
import boto3
import datetime
import decimal

    
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('yelp_restaurants')
i=0
while i<10:
    with open("Turkish restaurants{}.json".format(i),encoding="cp437") as json_file:
        restaurants = json.load(json_file, parse_float = decimal.Decimal)
        for restaurant in restaurants:
            
            data = {
                'Id': restaurant['id'],
                'Name': restaurant['name'],
                'Categories': restaurant['categories'],
                'Rating': int(restaurant['rating']),
                'Review_count': restaurant['review_count'],
                'Zip_code': restaurant['location']['zip_code'],
                'Address': restaurant['location']['display_address'],
                'Co-ordinates':restaurant['coordinates']
            }     
            
            table.put_item(
                Item={
                    'insertedAtTimestamp': str(datetime.datetime.now()),
                    'info': data,
                    'Id': data['Id']
                }
            )
            print (data['Name'])
            with open('restaurant_id.json', 'a+', encoding='utf-8') as f:
                json.dump(data['Id'], f, ensure_ascii=False, indent=4)
        i=i+1