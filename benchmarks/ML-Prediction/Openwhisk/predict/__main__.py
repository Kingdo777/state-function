import os
import json
import pickle
import boto3
from botocore.config import Config
import tensorflow as tf
import time

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless-test'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.jpg'


def timestamp(response, event, startTime, endTime):
    stampBegin = 1000 * time.time()
    prior = event['duration'] if 'duration' in event else 0
    response['duration'] = prior + endTime - startTime
    response['workflowEndTime'] = endTime
    response['workflowStartTime'] = event['workflowStartTime'] if 'workflowStartTime' in event else startTime
    priorCost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = priorCost - (stampBegin - 1000 * time.time())
    return response


def main(event):
    # Use S3 to communicate big messages
    # #####################################################################################################################
    s3 = boto3.client('s3', aws_access_key_id="AKIAW4QJVNK77MTUELIH",
                      aws_secret_access_key="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",
                      region_name="us-west-2",
                      config=Config(proxies={'https': 'http://222.20.94.67:7890'}))
    resize_pickle = s3.get_object(Bucket=BUCKET, Key=os.path.join(FOLDER, RESIZE_IMAGE))['Body'].read()
    # ######################################################################################################################
    print ("################################")
    startTime = 1000 * time.time()
    img = pickle.loads(resize_pickle)
    gd = tf.compat.v1.GraphDef.FromString(open('data/mobilenet_v2_1.0_224_frozen.pb', 'rb').read())

    inp, predictions = tf.import_graph_def(gd, return_elements=['input:0', 'MobilenetV2/Predictions/Reshape_1:0'])

    with tf.compat.v1.Session(graph=inp.graph):
        x = predictions.eval(feed_dict={inp: img})

    response = {
        "statusCode": 200,
        "body": json.dumps({'predictions': x.tolist()})
    }

    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == '__main__':
    print(main({}))
