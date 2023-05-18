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
File_KEY = 'faastlane/sentiment/{}'

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
    print("requestTime:{}".format(response['requestTime']))

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
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_KEY_ID,
                          region_name=S3_REGION_NAME,
                          config=Config(proxies={'https': 'http://192.168.162.239:7890'}))
    init_time += 1000 * time.time() - init_start_time

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        body_sentiment = redis_client.get("body_sentiment")
    elif op == "CB":
        body_sentiment = bucket.get_bytes("body_sentiment")
    elif op == "OW":
        body_sentiment = s3.get_object(Bucket=BUCKET, Key=File_KEY.format("body_sentiment"))['Body'].read()
    else:
        body_sentiment = event["body_sentiment"]
    transport_time += 1000 * time.time() - transport_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        body_sentiment = json.loads(body_sentiment)["body_sentiment"]
    else:
        body_sentiment = pickle.loads(body_sentiment)
    serialize_time += 1000 * time.time() - serialize_start_time

    execute_start_time = 1000 * time.time()
    '''
    Sends notification of negative results from sentiment analysis via SNS
    '''
    # construct message from input data and publish via SNS
    # sns = boto3.client('sns')
    # sns.publish(
    #    TopicArn = 'arn:aws:sns:XXXXXXXXXXXXXXXX:my-SNS-topic',
    #    Subject = 'Negative Review Received',
    #    Message = 'Review (ID = %i) of %s (ID = %i) received with negative results from sentiment analysis. Feedback from Customer (ID = %i): "%s"' % (int(event['body']['reviewID']),
    #                event['body']['reviewType'], int(event['body']['productID']), int(event['body']['customerID']), event['body']['feedback'])
    # )
    execute_time += 1000 * time.time() - execute_start_time

    return timestamp({}, event,
                     start_time,
                     execute_time,
                     serialize_time,
                     init_time,
                     transport_time)


if __name__ == "__main__":
    print(main(
        {'op': 'OW', 'endTime': 1684201797843.7585, 'requestTime': 216288.05908203125, 'executeTime': 3561.3447265625,
         'serializeTime': 257.97900390625, 'initTime': 501.893798828125, 'interactionTime': 10370.60986328125}
    ))
    # print(main(
    #     {'op': 'OFC', 'endTime': 1683985303160.1968, 'requestTime': 1474736.4560546875, 'executeTime': 298.7470703125,
    #      'serializeTime': 0.072509765625, 'initTime': 0.734619140625, 'interactionTime': 6.23876953125}))
    # print(main(
    #     {'op': 'FT',
    #      'body_sentiment': '{"body_sentiment": {"sentiment": 1, "reviewType": 0, "reviewID": "123", "customerID": "456", "productID": "789", "feedback": "Great product"}}',
    #      'endTime': 1683986211604.395, 'requestTime': 2382886.0346679688, 'executeTime': 317.211669921875,
    #      'serializeTime': 0.140869140625, 'initTime': 0.004150390625, 'interactionTime': 0.0029296875}))
    # print(main(
    #     {'op': 'CB', 'endTime': 1683985303190.9434, 'requestTime': 1474189.6872558594, 'executeTime': 294.21533203125,
    #      'serializeTime': 0.072021484375, 'initTime': 2.5537109375, 'interactionTime': 0.03955078125}
    # ))
