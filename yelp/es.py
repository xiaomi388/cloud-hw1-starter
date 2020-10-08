import elasticsearch
from elasticsearch import helpers
from requests_aws4auth import AWS4Auth
import boto3
import json

if __name__ == "__main__":
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(credentials.access_key, credentials.secret_key, "us-west-1", "es")
    es = elasticsearch.Elasticsearch(
        hosts=[{"host": 'search-cloud-hw1-hmeh2kicr4hcd4bbmpafzjg26a.us-west-1.es.amazonaws.com', "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=elasticsearch.RequestsHttpConnection
    )

    if es.indices.exists("restaurants"):
        es.indices.delete(index="restaurants")

    es.indices.create(index="restaurants", body={
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
        }, "mappings": {
            "properties": {
                "Restaurant": {
                    "properties": {
                        "id": {"type": "text"},
                        "cuisine": {"type": "text"}
                    }
                }
            }
        }
    })

    with open("./restaurants.json") as f:
        rs = json.load(f)
        actions = [
            {
                "_index": "restaurants",
                "_type": "_doc",
                "_id": r["id"],
                "_source": {
                    "Restaurant": {
                        "cuisine": r["cuisine"],
                        "id": r["id"]
                    }
                }
            }
            for r in rs.values()
        ]
        helpers.bulk(es, actions)






