from __future__ import print_function

import json
import os
import time

import boto3
from botocore.config import Config
import numpy as np
from PIL import Image
import pickle

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless-test'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.npy'

AWS_ACCESS_KEY_ID = "AKIAW4QJVNK77MTUELIH"
AWS_SECRET_KEY_ID = "UsFFYSX1t1klsi1+6p83+7wyhk9DWkK1sJiNTxAX"
S3_REGION_NAME = "us-west-2"


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
    startTime = 1000 * time.time()
    image = Image.open("data/image.jpg")
    img = np.array(image.resize((224, 224))).astype(np.float) / 128 - 1
    resize_img = img.reshape(1, 224, 224, 3)

    response = {"statusCode": 200}
    serialized_resize = pickle.dumps(resize_img)
    endTime = 1000 * time.time()
    # Baseline allows 1MB messages to be shared, use S3 to communicate messages
    # ######################################################################################################################
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_KEY_ID,
                      region_name=S3_REGION_NAME,
                      config=Config(proxies={'https': 'http://222.20.94.67:7890'}))

    s3response = s3.put_object(Bucket=BUCKET, Key=os.path.join(FOLDER, RESIZE_IMAGE), Body=serialized_resize)
    # ######################################################################################################################
    return timestamp(response, event, startTime, endTime)


if __name__ == '__main__':
    print(main(json.dumps(data)))
