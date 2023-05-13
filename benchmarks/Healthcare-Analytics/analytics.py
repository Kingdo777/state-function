import nltk

nltk.data.path.append('nltk_data/')
from nltk.tokenize import word_tokenize
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
        message = redis_client.get("masked_message").decode('utf-8')
    elif op == "CB":
        message = bucket.get("masked_message")
    elif op == "FT":
        message = event["masked_message"]
    else:
        message = event["masked_message"]
    transport_time += 1000 * time.time() - transport_start_time

    execute_start_time = 1000 * time.time()
    tokens = word_tokenize(message)
    execute_time += 1000 * time.time() - execute_start_time

    response = {
        "body": len(tokens)
    }
    print(start_time - event["endTime"])
    return timestamp(response, event,
                     start_time,
                     execute_time,
                     serialize_time,
                     init_time,
                     transport_time)


if __name__ == '__main__':
    data = {
        "op": "OW",
        "masked_message": "Pt is ## yo woman, ################## with past medical history that includes   - status post cardiac catheterization in ##########.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily, Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled"
    }
    print(main(data))

    data['op'] = 'FT'
    print(main(data))

    data = {'op': 'OFC'}
    print(main(data))

    data = {'op': 'CB'}
    print(main(data))
