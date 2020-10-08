import json
import boto3
import elasticsearch
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key
from credential import *


def lambda_handler(event, context):
    sns = boto3.client("sns", region_name="us-west-2")
    sqs = boto3.resource("sqs", region_name="us-west-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-west-1")
    table = dynamodb.Table('yelp-restaurants')
    credentials = boto3.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key).get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, "us-west-1", "es")
    es = elasticsearch.Elasticsearch(
        hosts=[{"host": 'search-cloud-hw1-hmeh2kicr4hcd4bbmpafzjg26a.us-west-1.es.amazonaws.com', "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=elasticsearch.RequestsHttpConnection
    )

    queue = sqs.get_queue_by_name(QueueName="cloud-hw1")
    for msg in queue.receive_messages():
        req = json.loads(msg.body)
        # query restaurant
        res = es.search(body={
            "query": {
                "function_score": {
                    "query": {
                        "match": {"Restaurant.cuisine": req["cuisine"]},
                    },
                    "random_score": {}
                },
            },
            "size": 3
        }, index="restaurants", doc_type="_doc")
        print(res)
        ids = [res["hits"]["hits"][i]["_id"] for i in range(3)]
        print(ids)
        restaurants = [q["Items"][0] for q in [table.query(KeyConditionExpression=Key("id").eq(rid)) for rid in ids]]
        print(restaurants)

        # send sms
        sns.publish(PhoneNumber=req["phone"], Message=(
            f"Hello! Here are my {req['cuisine']} restaurant "
            f"suggestions for {req['people']} people, for {req['date']} at {req['time']}: "
            f"1. {restaurants[0]['name']}, located at {''.join(restaurants[0]['location']['display_address'])}, "
            f"2. {restaurants[1]['name']}, located at {''.join(restaurants[1]['location']['display_address'])}, "
            f"3. {restaurants[2]['name']}, located at {''.join(restaurants[2]['location']['display_address'])}. "
            f"Enjoy your meal!"
        ))
        msg.delete()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == "__main__":
    lambda_handler(None, None)
