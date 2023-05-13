import json
import pickle
import time
import datetime

import redis
import datafunction as df
import boto3
from botocore.config import Config

BUCKET = 'kingdo-serverless'
IMG_KEY = 'faastlane/prediction-pipeline/img-resize/{}.npy'

AWS_ACCESS_KEY_ID = "AKIA2EGUEMCVKZGPBGIC"
AWS_SECRET_KEY_ID = "w9zEt8hTXOkKKbOIc+gWC8FaXfYAkm23b8YhOQ/3"
S3_REGION_NAME = "us-west-2"

global redis_client
global bucket
global s3


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
    global redis_client, bucket, s3
    op = event["op"]
    if op != "FT":
        index = event["index"]

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.get_bucket("kingdo")
    elif op == "FT":
        pass
    else:
        pass
    init_end_time = 1000 * time.time()

    execute_start_time = 1000 * time.time()
    portfolio = event['body']['portfolio']
    portfolios = json.loads(open('data/portfolios.json', 'r').read())
    data = portfolios[portfolio]
    valid = True
    for trade in data:
        trddate = trade['TradeDate']
        # Tag ID: 75, Tag Name: TradeDate, Format: YYMMDD
        if len(trddate) == 6:
            try:
                datetime.datetime(int(trddate[0:2]), int(trddate[2:4]), int(trddate[4:6]))
            except ValueError:
                valid = False
                break
        else:
            valid = False
            break
    data = {'valid': valid, 'portfolio': portfolio}
    execute_end_time = 1000 * time.time()

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        serialize_data = json.dumps( data)
    elif op == "OW":
        serialize_data = data
    else:
        serialize_data = pickle.dumps(data)
    serialize_end_time = 1000 * time.time()

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set('trddate_{}'.format(index), serialize_data)
    elif op == "CB":
        bucket.set('trddate_{}'.format(index), serialize_data)
    elif op == "FT":
        response["body"] = serialize_data
    else:
        response["body"] = serialize_data
    transport_end_time = 1000 * time.time()

    response["endTime"] = 1000 * time.time()
    return timestamp(response, event, 0,
                     execute_end_time - execute_start_time,
                     serialize_end_time - serialize_start_time,
                     init_end_time - init_start_time,
                     transport_end_time - transport_start_time)


if __name__ == "__main__":
    print(main({"op": "OW", "index": 0, "body": {"portfolio": "1234"}}))
    print(main({"op": "FT", "index": 0, "body": {"portfolio": "1234"}}))
    print(main({"op": "OFC", "index": 0, "body": {"portfolio": "1234"}}))
    print(main({"op": "CB", "index": 0, "body": {"portfolio": "1234"}}))
