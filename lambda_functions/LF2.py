import json
import boto3
import random
import requests
from requests_aws4auth import AWS4Auth

def get_sqs_message_attribute(msg, attr):
    return msg['MessageAttributes'][attr]['StringValue']

def get_sqs_queue_messages():
    # Create SQS client
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/581161247391/sqs_queue'
    
    # Receive message from SQS queue
    response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=2,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=10,
                WaitTimeSeconds=0
                )
    print(response)
    if "Messages" in response.keys():
        message = response['Messages']
    else:
        message = []
    return message

def delete_sqs_messages(receipt_handle):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/581161247391/sqs_queue'
    sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

def get_recommendations_from_elasticsearch(cuisine):
    print("Elastic Search")
    region = 'us-east-1' 
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = ''
    index = ''
    url = 'https://' + host + '/' + index + '/_search'
    url = 'https://search-dining-concierge-chatbot-xwlf5gjwkmqmggvmawl36nit4i.us-east-1.es.amazonaws.com/restaurants/_search'
    query = {
                "size": 10,
                "query": {
                    "query_string": {
                      "default_field": "cuisines",
                      "query": cuisine
                    }
                }
            }

    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    response = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    return json.loads(response.text)

def parse_restaurant_list(recommendation):
    restaurant_id_list = []
    rest_hits = recommendation["hits"]["hits"]
    for res in rest_hits:
        restaurant_id_list.append(res["_source"]['restaurant_id'])
    return restaurant_id_list

def get_restaurant_details(restaurants):
    print("Dynamo DB")
    restaurant_list = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp_restaurants')
    for restaurant in restaurants:
        response = table.get_item(Key={'Id' : restaurant})
        restaurant_list.append(response)
    print(restaurant_list)
    return restaurant_list

def parsed_restaurant_details(restaurant_details):
    rest_text = ''
    count = 3 if len(restaurant_details) >= 3 else len(restaurant_details)
    random_rest = random.sample(restaurant_details, count)
    for i in range(len(random_rest)):
        rest_name = random_rest[i]['Item']['info']['Name']
        rest_addr = random_rest[i]['Item']['info']['Address'][0]
        rest_text = rest_text + ' %s. %s located at %s.' %((i+1), rest_name, rest_addr)
    return rest_text
    
def send_text_message(phone_num, text):
    client = boto3.client('sns')
    response = client.publish(PhoneNumber=phone_num, Message=text)

def lambda_handler(event, context):
    sqs_messages = get_sqs_queue_messages()
    for msg in sqs_messages:
        receipt_handle = msg['ReceiptHandle']
        cuisine = get_sqs_message_attribute(msg, attr='cuisine')
        date = get_sqs_message_attribute(msg, attr='date')
        location = get_sqs_message_attribute(msg, attr='location')
        numPeople = get_sqs_message_attribute(msg, attr='numPeople')
        phone_num = get_sqs_message_attribute(msg, attr='phone')
        time = get_sqs_message_attribute(msg, attr='time')
        recommendation = get_recommendations_from_elasticsearch(cuisine)
        restaurant_id_list = parse_restaurant_list(recommendation)
        #restaurant_id_list = ['1KGvtMU7VBcdlvxo2brdQg']
        if restaurant_id_list:
            restaurant_details = get_restaurant_details(restaurant_id_list)
            restaurant_reccom = parsed_restaurant_details(restaurant_details)
            text_message = "Hello! Here are my %s restaurant suggestions for %s people, for %s %s : %s" %(cuisine, numPeople, date, time, restaurant_reccom) 
        else:
            text_message = "Sorry, we were unable to find any restaurants for %s in %s. We regret for the inconvenience" %(cuisine, location, time, restaurant_reccom) 
        print(text_message)
        if "+1" not in phone_num:
            phone_num  = '+1'+phone_num
        print(phone_num)
        send_text_message(phone_num, text_message)
        delete_sqs_messages(receipt_handle)
        
    

