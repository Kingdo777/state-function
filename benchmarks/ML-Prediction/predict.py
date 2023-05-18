import json
import pickle
import tensorflow as tf
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
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_KEY_ID,
                          region_name=S3_REGION_NAME,
                          config=Config(proxies={'https': 'http://192.168.162.239:7890'}))
    init_time += 1000 * time.time() - init_start_time

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        resize_img_list = redis_client.get("ml_predict")
    elif op == "CB":
        resize_img_list = bucket.get_bytes("ml_predict")
    elif op == "FT":
        resize_img_list = event["ml_predict"]
    else:
        resize_img_list = s3.get_object(Bucket=BUCKET, Key=IMG_KEY.format("ml_predict"))['Body'].read()
    transport_time += 1000 * time.time() - transport_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        img = np.array(json.loads(resize_img_list)["resize_img_list"][0])
    else:
        img = pickle.loads(resize_img_list)[0]
    serialize_time += 1000 * time.time() - serialize_start_time

    execute_start_time = 1000 * time.time()
    gd = tf.compat.v1.GraphDef.FromString(open('data/mobilenet_v2_1.0_224_frozen.pb', 'rb').read())
    inp, predictions = tf.import_graph_def(gd, return_elements=['input:0', 'MobilenetV2/Predictions/Reshape_1:0'])
    with tf.compat.v1.Session(graph=inp.graph):
        x = predictions.eval(feed_dict={inp: img})
    execute_time += 1000 * time.time() - execute_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        x_data = json.dumps({'predictions': x.tolist()})
    else:
        x_data = pickle.dumps(x)
    serialize_time += 1000 * time.time() - serialize_start_time

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set("ml_render", x_data)
    elif op == "CB":
        bucket.set("ml_render", x_data)
    elif op == "FT":
        response["ml_render"] = x_data
    else:
        s3.put_object(Bucket=BUCKET, Key=IMG_KEY.format("ml_render"), Body=x_data)
    transport_time += 1000 * time.time() - transport_start_time

    response["endTime"] = 1000 * time.time()
    response["Time-Breakdown-Predict"] = response["endTime"] - start_time
    response["Time-Breakdown-Resize"] = event["Time-Breakdown-Resize"]
    return timestamp(response, event,
                     start_time,
                     execute_time,
                     serialize_time,
                     init_time,
                     transport_time)


if __name__ == '__main__':
    print(main({"op": "OFC"}))
    # print(main({"op": "CB"}))
    # print(main({"op": "OW"}))
