from __future__ import print_function

import time

import numpy as np
from PIL import Image
import pickle
import datafunction as df

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless-test'
FOLDER = 'faastlane/prediction-pipeline'
IMAGE = 'img-src/panda.jpg'
RESIZE_IMAGE = 'img-resize/panda-resize.npy'

AWS_ACCESS_KEY_ID = "AKIAW4QJVNK77MTUELIH"
AWS_SECRET_KEY_ID = "UsFFYSX1t1klsi1+6p83+7wyhk9DWkK1sJiNTxAX"
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
    # execute function code
    # **********************************************************************************************************************
    execute_start_time = 1000 * time.time()
    image = Image.open("data/image.jpg")
    img = np.array(image.resize((224, 224))).astype(np.float) / 128 - 1
    resize_img = img.reshape(1, 224, 224, 3)

    response = {"statusCode": 200}
    serialized_resize = pickle.dumps(resize_img)
    bucket = df.create_bucket("kingdo", 1024 * 1024 * 5)
    execute_end_time = 1000 * time.time()
    # **********************************************************************************************************************

    # use DataFunction to communicate messages
    # ######################################################################################################################
    transport_start_time = execute_end_time
    bucket.set("body", serialized_resize)
    transport_end_time = 1000 * time.time()
    # ######################################################################################################################

    return timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time)


if __name__ == '__main__':
    print(main({}))