import json, os
import numpy as np
import tensorflow as tf
import time

from utils import timestamp

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless-test'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.jpg'


def main(event):
    startTime = 1000 * time.time()
    body = json.loads(event['body'])
    img = np.array(body['resize_img'])
    del body

    gd = tf.compat.v1.GraphDef.FromString(open('data/mobilenet_v2_1.0_224_frozen.pb', 'rb').read())

    inp, predictions = tf.import_graph_def(gd, return_elements=['input:0', 'MobilenetV2/Predictions/Reshape_1:0'])

    with tf.compat.v1.Session(graph=inp.graph):
        x = predictions.eval(feed_dict={inp: img})

    response = {
        "statusCode": 200,
        "body": json.dumps({'predictions': x.tolist()})
    }

    endTime = 1000 * time.time()

    response["predictExecuteTime"] = endTime - startTime
    response["resizeExecuteTime"] = event["resizeExecuteTime"]
    return timestamp(response, event, startTime, endTime)
