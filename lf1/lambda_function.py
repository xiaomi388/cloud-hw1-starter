import math
import dateutil.parser
import datetime
import time
import os
import logging
import json
import boto3


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

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

def close(session_attributes, fulfillment_state, slots):
    sqs = boto3.resource('sqs', region_name='us-west-1')
    queue = sqs.get_queue_by_name(QueueName='cloud-hw1')
    response = queue.send_message(MessageBody=json.dumps(slots))
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state
        }
    }

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def is_valid_cuisine(cuisine):
    cuisine_types = ["Chinese", "Indian", "Japanese", "Mexican", "Thai", "Italian", "Vietnamese", "American"]
    is_valid = False
    for i in cuisine_types:
        if i.lower() in cuisine.lower():
            is_valid = True
    return  is_valid

def validate_dining_suggestions(location,diningTime,phoneNumber,numberOfPeople,diningDate,cuisine):
    if cuisine is not None and not is_valid_cuisine(cuisine):
        return build_validation_result(False,
                                       'Cuisine',
                                       'Please give another type of cuisine. We provide search for Chinese, Indian, Japanese, Mexican, Thai, Italian, Vietnamese and American food.')
                                       
    if numberOfPeople is not None :
        if int(numberOfPeople) <= 0:
            return build_validation_result(False, 'NumberOfPeople', 'Please provide a positive number of people in your party.')

    if diningDate is not None:
        if not isvalid_date(diningDate):
            return build_validation_result(False, 'DiningDate', 'I did not understand that, what date would you like to dine?')
        elif datetime.datetime.strptime(diningDate, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'DiningDate', 'Please provide a valid data, i.e. from today and onwords.')

    if diningTime is not None:
        if len(diningTime) != 5:
            return build_validation_result(False, 'DiningTime', None)

        hour, minute = diningTime.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            return build_validation_result(False, 'DiningTime', None)
        now = datetime.datetime.now().strftime("%H:%M")
        if diningTime <= now:
            return build_validation_result(False, 'DiningTime', None)

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """

def dining_suggestions_intent(intent_request):

    location = get_slots(intent_request)["Location"]
    diningTime = get_slots(intent_request)["DiningTime"]
    phoneNumber = get_slots(intent_request)["PhoneNumber"]
    numberOfPeople = get_slots(intent_request)["NumberOfPeople"]
    diningDate = get_slots(intent_request)["DiningDate"]
    cuisine = get_slots(intent_request)["Cuisine"]
    source = intent_request['invocationSource']


    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_dining_suggestions(location,diningTime,phoneNumber,numberOfPeople,diningDate,cuisine)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
 
        return delegate(output_session_attributes, get_slots(intent_request))
        
    if source == 'FulfillmentCodeHook':
        slots = get_slots(intent_request)

        validation_result = validate_dining_suggestions(location,diningTime,phoneNumber,numberOfPeople,diningDate,cuisine)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

    return close(intent_request['sessionAttributes'],'Fulfilled',get_slots(intent_request))


""" --- Intents --- """

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggestions_intent(intent_request)
    elif intent_name == 'GreetingIntent' or intentName == 'ThankYouIntent':
        return {
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled'
                }
            }

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    return dispatch(event)
