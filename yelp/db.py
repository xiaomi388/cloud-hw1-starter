import requests
import json
import boto3
import copy
from decimal import *
from datetime import datetime

API_KEY = ("e-DK7dnHFQttY_ikS7Ld4NRx83iapbQhrCB06GUJ_NEemJRl7vAjtlOMaf7Wp-"
           "qf1kgidF0H51xaQ95ucZW_itHO3NpTxdCbu5w5luLSNTD6dz44KcUrFAQ8syV8X3Yx")
CUISINE_TYPES = ["Chinese", "Indian", "Japanese", "Mexican", "Thai", "Italian", "Vietnamese", "American"]


def put_restaurant(r):
    # put restaurant in elasticsearch

    # put restaurant in dynamodb
    dynamodb = boto3.resource('dynamodb', region_name="us-west-1")
    table = dynamodb.Table('yelp-restaurants')

    def convert(obj):
        if isinstance(obj, list):
            for i in range(len(obj)):
                if isinstance(obj[i], float):
                    obj[i] = Decimal(str(obj[i]))
                elif isinstance(obj[i], dict):
                    convert(obj[i])
                elif isinstance(obj[i], list):
                    convert(obj[i])
        elif isinstance(obj, dict):
            for key in obj:
                if isinstance(obj[key], float):
                    obj[key] = Decimal(str(obj[key]))
                elif isinstance(obj[key], dict):
                    convert(obj[key])
                elif isinstance(obj[key], list):
                    convert(obj[key])

    rr = copy.deepcopy(r)
    convert(rr)
    rr["insertedAtTimestamp"] = int(datetime.now().timestamp())
    table.put_item(Item=rr)



def get_restaurants(term, offset):
    url = "https://api.yelp.com/v3/businesses/search"
    res = requests.get(url, params={
        "term": term,
        "location": "Manhattan",
        "limit": 50,
        "offset": offset,
    }, headers={
        "Authorization": f"Bearer {API_KEY}"
    }).json()
    return res["businesses"] if "businesses" in res else []


def resume():
    with open("./restaurants.json") as f:
        restaurants = json.load(f)
    with open('./process.json') as f:
        init_cuisine_index, init_offset, init_cnt = json.load(f)
    return restaurants, init_cuisine_index, init_offset, init_cnt


def main():
    restaurants, init_cuisine_index, init_offset, init_cnt = resume()

    cuisine_index, cnt, offset = init_cuisine_index, init_cnt, init_offset
    try:
        for cuisine_index in range(init_cuisine_index, len(CUISINE_TYPES)):
            while cnt < 1000:
                rs = get_restaurants(f"{CUISINE_TYPES[cuisine_index]} restaurants", offset)
                if not rs:
                    break
                for r in rs:
                    if r["id"] in restaurants:
                        continue
                    r["cuisine"] = CUISINE_TYPES[cuisine_index]
                    put_restaurant(r)
                    restaurants[r["id"]] = r
                    cnt += 1
                    print(cuisine_index, cnt, offset)
                offset += 50
            cnt, offset = 0, 0
    finally:
        with open("./restaurants.json", "w") as f:
            json.dump(restaurants, f, ensure_ascii=False)
        with open("./process.json", "w") as f:
            json.dump((cuisine_index, offset, cnt), f)
        print(len(restaurants))


if __name__ == "__main__":
    main()
