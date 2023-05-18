import json
import pickle

import numpy as np
import time
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
              execute_start_time,
              execute_end_time,
              serialize_start_time,
              serialize_end_time,
              init_start_time, init_end_time,
              transport_start_time, transport_end_time):
    prior_request_time = event['requestTime'] if 'requestTime' in event else 0
    response['requestTime'] = prior_request_time + start_time - event['endTime']

    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_end_time - execute_start_time

    prior_serialize_time = event['serializeTime'] if 'serializeTime' in event else 0
    response['serializeTime'] = prior_serialize_time + serialize_end_time - serialize_start_time

    prior_init_time = event['initTime'] if 'initTime' in event else 0
    response['initTime'] = prior_init_time + init_end_time - init_start_time

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    return response


def main(event):
    start_time = 1000 * time.time()

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
    init_end_time = 1000 * time.time()

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        x_data = redis_client.get("ml_render")
    elif op == "CB":
        x_data = bucket.get_bytes("ml_render")
    elif op == "FT":
        x_data = event["ml_render"]
    else:
        x_data = s3.get_object(Bucket=BUCKET, Key=IMG_KEY.format("ml_render"))['Body'].read()
    transport_end_time = 1000 * time.time()

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        x = np.array(json.loads(x_data)["predictions"])
    else:
        x = pickle.loads(x_data)
    serialize_end_time = 1000 * time.time()

    execute_start_time = 1000 * time.time()
    text = "Top 1 Prediction: " + str(x.argmax()) + str(x.max())
    execute_end_time = 1000 * time.time()

    response = {
        "body": text,
        "Time-Breakdown": {
            "Resize": event["Time-Breakdown-Resize"],
            "Predict": event["Time-Breakdown-Predict"],
            "Render": execute_end_time - start_time
        }
    }
    return timestamp(response, event, start_time,
                     execute_start_time, execute_end_time,
                     serialize_start_time, serialize_end_time,
                     init_start_time, init_end_time,
                     transport_start_time, transport_end_time)


if __name__ == '__main__':
    print(main({"op": "OFC"}))
    # print(main({"op": "OW"}))
