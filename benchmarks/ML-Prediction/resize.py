from __future__ import print_function

import json
import time

import numpy as np
from PIL import Image
import pickle
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
              execute_start_time,
              execute_end_time,
              serialize_start_time,
              serialize_end_time,
              init_start_time, init_end_time,
              transport_start_time, transport_end_time):
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
    global redis_client, bucket, s3
    op = event["op"]

    execute_start_time = 1000 * time.time()
    resize_img_list = []
    for i in range(1, 4):
        image = Image.open("data/image{}.jpg".format(i))
        img = np.array(image.resize((224, 224))).astype(float) / 128 - 1
        resize_img = img.reshape(1, 224, 224, 3)
        resize_img_list.append(resize_img)
    execute_end_time = 1000 * time.time()

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        resize_img_list_ = []
        for img in resize_img_list:
            resize_img_list_.append(img.tolist())
        serialized_data = json.dumps({"resize_img_list": resize_img_list_})
    else:
        serialized_data = pickle.dumps(resize_img_list)
    print(len(serialized_data) / 1024)
    serialize_end_time = 1000 * time.time()

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.create_bucket("kingdo", 1024 * 1024 * 4)
    elif op == "FT":
        pass
    else:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_KEY_ID,
                          region_name=S3_REGION_NAME,
                          config=Config(proxies={'https': 'http://192.168.162.239:7890'}))
    init_end_time = 1000 * time.time()

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set("ml_predict", serialized_data)
    elif op == "CB":
        bucket.set("ml_predict", serialized_data)
    elif op == "FT":
        response["ml_predict"] = serialized_data
    else:
        s3.put_object(Bucket=BUCKET, Key=IMG_KEY.format("ml_predict"), Body=serialized_data)
    transport_end_time = 1000 * time.time()

    response["endTime"] = 1000 * time.time()
    response["Time-Breakdown-Resize"] = response["endTime"] - execute_start_time
    print(init_end_time - init_start_time)
    return timestamp(response, event,
                     execute_start_time, execute_end_time,
                     serialize_start_time, serialize_end_time,
                     init_start_time, init_end_time,
                     transport_start_time, transport_end_time)


if __name__ == '__main__':
    print(main({"op": "OFC"}))
    print(main({"op": "CB"}))
    print(main({"op": "OW"}))
    result = main({"op": "FT"})
    result.pop("ml_predict")
    print(result)
