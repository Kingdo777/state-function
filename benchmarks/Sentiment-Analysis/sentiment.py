import json

import nltk
import pickle
import time
import boto3
import time

from botocore.config import Config
import redis
import datafunction as df

BUCKET = 'kingdo-serverless'
IMG_KEY = 'faastlane/prediction-pipeline/img-resize/{}.npy'

AWS_ACCESS_KEY_ID = "AKIA2EGUEMCVKZGPBGIC"
AWS_SECRET_KEY_ID = "w9zEt8hTXOkKKbOIc+gWC8FaXfYAkm23b8YhOQ/3"
S3_REGION_NAME = "us-west-2"

global redis_client
global bucket
global s3

nltk.data.path.append('nltk_data/')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def timestamp(response, event,
              start_time,
              execute_time,
              serialize_time,
              init_time,
              transport_time):
    if 'requestTime' in event:
        prior_request_time = event['requestTime'] if 'requestTime' in event else 0
        response['requestTime'] = prior_request_time + start_time - event['endTime']
    else:
        response['requestTime'] = 0

    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_time

    prior_serialize_time = event['serializeTime'] if 'serializeTime' in event else 0
    response['serializeTime'] = prior_serialize_time + serialize_time

    prior_init_time = event['initTime'] if 'initTime' in event else 0
    response['initTime'] = prior_init_time + init_time

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_time

    return response


def main(event):
    start_time = 1000 * time.time()
    init_time = 0
    execute_time = 0
    serialize_time = 0
    transport_time = 0

    global redis_client, bucket, s3
    op = event["op"]

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.get_bucket("kingdo")
    elif op == "FT":
        pass
    else:
        pass
    init_time += 1000 * time.time() - init_start_time

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        body = redis_client.get("body")
    elif op == "CB":
        body = bucket.get_bytes("body")
    else:
        body = event["body"]
    transport_time += 1000 * time.time() - transport_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        body = json.loads(body)["body"]
    elif op == "OW":
        pass
    else:
        body = pickle.loads(body)
    serialize_time += 1000 * time.time() - serialize_start_time

    execute_start_time = 1000 * time.time()
    sid = SentimentIntensityAnalyzer()
    feedback = body['feedback']
    scores = sid.polarity_scores(feedback)
    if scores['compound'] > 0:
        sentiment = 1
    elif scores['compound'] == 0:
        sentiment = 0
    else:
        sentiment = -1

    body_sentiment = {'sentiment': sentiment,
                      'reviewType': body['reviewType'] + 0,
                      'reviewID': (body['reviewID'] + '0')[:-1],
                      'customerID': (body['customerID'] + '0')[:-1],
                      'productID': (body['productID'] + '0')[:-1],
                      'feedback': (body['feedback'] + '0')[:-1]}
    execute_time += 1000 * time.time() - execute_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        serialize_data = json.dumps({"body_sentiment": body_sentiment})
    elif op == "OW":
        serialize_data = body_sentiment
    else:
        serialize_data = pickle.dumps(body_sentiment)
    serialize_time += 1000 * time.time() - serialize_start_time

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set("body_sentiment", serialize_data)
    elif op == "CB":
        bucket.set("body_sentiment", serialize_data)
    else:
        response["body_sentiment"] = serialize_data
    transport_time += 1000 * time.time() - transport_start_time

    response["endTime"] = 1000 * time.time()
    return timestamp(response, event,
                     start_time,
                     execute_time,
                     serialize_time,
                     init_time,
                     transport_time)


if __name__ == "__main__":
    result = main({'op': 'OW', 'body': {'reviewType': 0, 'reviewID': '123', 'customerID': '456', 'productID': '789',
                                        'feedback': 'Great product'}, 'endTime': 1683984881731.7017, 'requestTime': 0,
                   'executeTime': 284.338134765625, 'serializeTime': 0.025390625, 'initTime': 0.00048828125,
                   'interactionTime': 0.0009765625})
    print(result)
    result.pop('body_sentiment')
    print(result)

    print(main({'op': 'OFC', 'endTime': 1683983828400.8694, 'requestTime': 0, 'executeTime': 279.18212890625,
                'serializeTime': 0.03369140625, 'initTime': 0.376953125, 'interactionTime': 3.33984375}))

    result = main({'op': 'FT',
                   'body': '{"body": {"reviewType": 0, "reviewID": "123", "customerID": "456", "productID": "789", "feedback": "Great product"}}',
                   'endTime': 1683983828704.32, 'requestTime': 0, 'executeTime': 303.250732421875,
                   'serializeTime': 0.070068359375, 'initTime': 0.0029296875, 'interactionTime': 0.0009765625})
    print(result)
    result.pop('body_sentiment')
    print(result)

    print(main({'op': 'CB', 'endTime': 1683983828985.679, 'requestTime': 0, 'executeTime': 280.014892578125,
                'serializeTime': 0.042236328125, 'initTime': 1.24169921875, 'interactionTime': 0.0146484375}))
