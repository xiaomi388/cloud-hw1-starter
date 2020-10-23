import json
import boto3

def lambda_handler(event, context):
    print(event['currentIntent']['slots'])
    sqs = boto3.resource('sqs', region_name='us-west-1')
    queue = sqs.get_queue_by_name(QueueName='cloud-hw1')
    response = queue.send_message(MessageBody=json.dumps(event['currentIntent']['slots']))
    print(response)
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled'
        }
    }
