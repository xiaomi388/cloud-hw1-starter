# Chatbot Concierge #

## Team Members

Shiqi Fan: snf2125 snf2125@columbia.edu

Yufan Chen:  yc3858 yc3858@columbia.edu


## Folder Structure

- api gateway: contains the swagger file for the api gateway. 
the api gateway service is located in region us-west-1
- lf0: lambda function, located in region us-west-1
- lf1: lambda function, located in region us-east-1
- lf2: lambda function, located in region us-west-1
- s3: the frontend code, located in region us-west-1
- yelp:
    - db.py: scrape restaurants from yelp and save 
    restaurants into `restaurants.json`, then push all
    data to aws dynamodb
    - es.py: read data from `restaurants.json`, then push
    cuisine and id of every restaurant to aws elasticsearch
    - the dynamodb service is located in us-west-1
    - the elasticsearch service is located in us-west-1

