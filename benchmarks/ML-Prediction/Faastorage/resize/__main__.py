from __future__ import print_function

import time

import numpy as np
from PIL import Image
import pickle
import datafunction as df


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
    img = np.array(image.resize((224, 224))).astype(float) / 128 - 1
    resize_img = img.reshape(1, 224, 224, 3)

    response = {"statusCode": 200}
    serialized_resize = pickle.dumps(resize_img)
    execute_end_time = 1000 * time.time()
    # **********************************************************************************************************************

    # use DataFunction to communicate messages
    # ######################################################################################################################
    transport_start_time = execute_end_time
    bucket = df.create_bucket("kingdo", 1024 * 1024 * 5)
    bucket.set("body", serialized_resize)
    transport_end_time = 1000 * time.time()
    # ######################################################################################################################

    response["resizeExecuteTime"] = execute_end_time - execute_start_time
    return timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time)


if __name__ == '__main__':
    print(main({}))
