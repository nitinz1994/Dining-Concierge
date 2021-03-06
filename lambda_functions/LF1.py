import json
import os
import math
import dateutil.parser
import datetime
import time
import logging
import boto3
from botocore.vendored import requests
import string

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    return response
    
def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def isvalid_location(location):
    locations = ['new york', 'manhattan']
    if location.lower() not in locations:
        return build_validation_result(False,
                                       'Location',
                                       'Please enter correct location. We offer service only in Manhattan currently')

def isvalid_cuisine(cuisine):
    cuisines = ['indian','thai','thaiwanese','american','brazillian','chinese','cuban','irish','italian','mexican','turkish','greek']
    if cuisine.lower() not in cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'Please enter a correct Cuisine')

def isvalid_people(num_people):
    print("num people", num_people)
    num_people = int(num_people)
    if num_people > 100 or num_people < 1:
        return build_validation_result(False,
                                  'Count',
                                  'Range of 1 to 100 people allowed')

def isvalid_phonenum(phone_num):
    if len(phone_num)!= 10 and (phone_num.startswith('+1') is False and len(phone_num) != 12):
        return build_validation_result(False, 'PhoneNumber', 'Phone Number must be in form +1xxxxxxxxxx or a 10 digit number')
    elif len(phone_num) == 10 and (phone_num.startswith('+1') is True):
        return build_validation_result(False, 'PhoneNumber', 'Phone Number must be in form +1xxxxxxxxxx or a 10 digit number')
        
    
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def greeting_intent(intent_request):
    
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText', 
                'content': 'Hey there, how can I help?'}
        }
    }

def thank_you_intent(intent_request):
    return {
        'dialogAction': {
            "type": "ElicitIntent",
            'message': {
                'contentType': 'PlainText', 
                'content': "You are welcome !"}
        }
    }

def validate_dining_suggestion(location, cuisine, num_people, date, given_time, phone_num):
    
    
    if location is not None: 
        notValidLocation = isvalid_location(location)
        if notValidLocation:
            return notValidLocation

    if cuisine is not None:
        notValidCuisine = isvalid_cuisine(cuisine)
        if notValidCuisine:
            return notValidCuisine
        
                                       
    if num_people is not None:
        notValidPeople = isvalid_people(num_people)
        if notValidPeople:
            return notValidPeople

    if date is not None:      
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'Please enter correct date in yyyy/mm/dd form')

        if datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Date', 'Please enter date from today')
        
        
    
    if given_time is not None:
        print("given_time", given_time)

    if phone_num is not None:
        notValidPhonenum = isvalid_phonenum(phone_num)
        if notValidPhonenum:
            return notValidPhonenum

    return build_validation_result(True, None, None)

def dining_suggestion_intent(intent_request):
    
    location = get_slots(intent_request)["Location"]
    cuisine = get_slots(intent_request)["Cuisine"]
    given_time = get_slots(intent_request)["Time"]
    date = get_slots(intent_request)["Date"]
    num_people = get_slots(intent_request)["Count"]
    phone = get_slots(intent_request)["PhoneNumber"]
    
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)
        
        validation_result = validate_dining_suggestion(location, cuisine, num_people, date, given_time, phone)
        print ("validation_result", validation_result)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
                               
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

        print("output_session_attributes", output_session_attributes)
        
        return delegate(output_session_attributes, get_slots(intent_request))
      
    requestData = {
                    "cuisine":cuisine,
                    "location":location,
                    "limit":"3",
                    "numPeople": num_people,
                    "date" : date,
                    "time": given_time,
                    "phone" : phone
                }
                
    print (requestData)
    
    
    messageId = restaurantSQSRequest(requestData)
    print (messageId)

    return close(intent_request['sessionAttributes'],
             'Fulfilled',
             {'contentType': 'PlainText',
              'content': 'I have received your request and will be sending the suggestions shortly. Have a Great Day !!'})


def restaurantSQSRequest(requestData):
    
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/581161247391/sqs_queue'
    delaySeconds = 5
    messageAttributes = {
        'cuisine': {
            'DataType': 'String',
            'StringValue': requestData['cuisine']
        },
        'location': {
            'DataType': 'String',
            'StringValue': requestData['location']
        },
        "time": {
            'DataType': "String",
            'StringValue': requestData['time']
        },
        "date": {
            'DataType': "String",
            'StringValue': requestData['date']
        },
        'numPeople': {
            'DataType': 'Number',
            'StringValue': requestData['numPeople']
        },
        'phone': {
            'DataType' : 'String',
            'StringValue' : requestData['phone']
        }
    }
    messageBody=('Recommendation for the food')
    
    response = sqs.send_message(
        QueueUrl = queue_url,
        DelaySeconds = delaySeconds,
        MessageAttributes = messageAttributes,
        MessageBody = messageBody
        )

    print("response", response)
    
    print ('send data to queue')
    print(response['MessageId'])
    
    return response['MessageId']

def dispatch(intent_request):

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    print(intent_name)

    if intent_name == 'GreetingIntent':
        return greeting_intent(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return dining_suggestion_intent(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you_intent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
