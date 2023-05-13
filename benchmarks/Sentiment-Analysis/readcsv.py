import json
import pickle
import time
import csv

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
        bucket = df.create_bucket("kingdo", 4096 * 1)
    elif op == "FT":
        pass
    else:
        pass
    init_time += 1000 * time.time() - init_start_time

    execute_start_time = 1000 * time.time()
    with open('data/few_reviews.csv') as csvFile:
        # DictReader -> convert lines of CSV to OrderedDict
        for row in csv.DictReader(csvFile):
            # return just the first loop (row) results!
            body = {}
            for k, v in row.items():
                body[k] = int(v) if k == 'reviewType' else v
    execute_time += 1000 * time.time() - execute_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        serialize_data = json.dumps({"body": body})
    elif op == "OW":
        serialize_data = body
    else:
        serialize_data = pickle.dumps(body)
    print(len(serialize_data) / 1024)
    serialize_time += 1000 * time.time() - serialize_start_time

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set("body", serialize_data)
    elif op == "CB":
        bucket.set("body", serialize_data)
    else:
        response["body"] = serialize_data
    transport_time += 1000 * time.time() - transport_start_time

    response["endTime"] = 1000 * time.time()
    return timestamp(response, event,
                     start_time,
                     execute_time,
                     serialize_time,
                     init_time,
                     transport_time)


if __name__ == "__main__":
    print(main({"op": "OW"}))
    print(main({"op": "OFC"}))
    print(main({"op": "FT"}))
    print(main({"op": "CB"}))
