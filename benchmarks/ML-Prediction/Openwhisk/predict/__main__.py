import os
import json
import pickle
import boto3
from botocore.config import Config
import tensorflow as tf
import time

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.npy'

AWS_ACCESS_KEY_ID = "AKIA2EGUEMCVKZGPBGIC"
AWS_SECRET_KEY_ID = "w9zEt8hTXOkKKbOIc+gWC8FaXfYAkm23b8YhOQ/3"
S3_REGION_NAME = "us-west-2"


def timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time):
    stamp_begin = 1000 * time.time()
    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_end_time - execute_start_time

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    prior_cost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = prior_cost - (stamp_begin - 1000 * time.time())
    return response


def main(event):
    print("KKKK {}".format(time.time() * 1000 - event['end']))
    # Use S3 to communicate big messages
    # #####################################################################################################################
    transport_start_time = 1000 * time.time()
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_KEY_ID,
                      region_name=S3_REGION_NAME,
                      config=Config(proxies={'https': 'http://192.168.162.239:7890'}))
    resize_pickle = s3.get_object(Bucket=BUCKET, Key=os.path.join(FOLDER, RESIZE_IMAGE))['Body'].read()
    transport_end_time = 1000 * time.time()
    # ######################################################################################################################

    # execute function code
    # **********************************************************************************************************************
    execute_start_time = transport_end_time
    img = pickle.loads(resize_pickle)
    gd = tf.compat.v1.GraphDef.FromString(open('data/mobilenet_v2_1.0_224_frozen.pb', 'rb').read())
    inp, predictions = tf.import_graph_def(gd, return_elements=['input:0', 'MobilenetV2/Predictions/Reshape_1:0'])
    with tf.compat.v1.Session(graph=inp.graph):
        x = predictions.eval(feed_dict={inp: img})
    response = {
        "statusCode": 200,
        "body": json.dumps({'predictions': x.tolist()})
    }
    execute_end_time = 1000 * time.time()
    # **********************************************************************************************************************

    return timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time)


if __name__ == '__main__':
    result = main({})

    print(result["executeTime"])
