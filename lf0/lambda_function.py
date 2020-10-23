import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('lex-runtime', region_name='us-east-1')
    temp = json.loads(event['body'])
    response = client.post_text(
        botName= 'Concierge',
        botAlias= 'conicerge',
        userId= 'user1',
        inputText= temp['messages'][0]['unstructured']['text']
    )
    print(response)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'messages':[ 
                {
                    'type': "unstructured", 
                    'unstructured': {'text': response['message']} 
                } 
            ] 
        })
    }