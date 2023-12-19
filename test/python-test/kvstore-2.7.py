import base64
import json
import os
import statefunction as df
import pickle
import time
import numpy as np
from PIL import Image


def write():
    bucket_create = df.create_bucket("kingdo", 40960)
    bucket_create.set("apple", "12")
    bucket_create.set("banana", "13")
    bucket_create.set("mum", "kiss")
    bucket_create.set("dad", b"fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol")
    bucket_create.set("apple1", "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol")
    bucket_create.set("banana1", "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol")
    bucket_create.set("mum1", "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol")


def read(destroy=False):
    bucket_get = df.get_bucket("kingdo")
    print(bucket_get.get("apple"))
    print(bucket_get.get("banana"))
    print(bucket_get.get("mum"))
    print(bucket_get.get("dad"))
    print(bucket_get.get("apple1"))
    print(bucket_get.get("banana1"))
    print(bucket_get.get("mum1"))
    if destroy:
        bucket_get.destroy()


def timestamp(response, event, startTime, endTime):
    stampBegin = 1000 * time.time()
    prior = event['duration'] if 'duration' in event else 0
    response['duration'] = prior + endTime - startTime
    response['workflowEndTime'] = endTime
    response['workflowStartTime'] = event['workflowStartTime'] if 'workflowStartTime' in event else startTime
    priorCost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = priorCost - (stampBegin - 1000 * time.time())
    print(response["duration"])
    return response


def read_write_test():
    write()
    if os.fork() == 0:
        print("In Child")
        read()
    else:
        os.wait()
        print("In Father")
        read(True)

    print("OK!!!")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # read_write_test()

    image = Image.open("/home/kingdo/CLionProjects/StateFunction/benchmarks/ML-Prediction/Faastlane/data/image.jpg")
    image_resize = image.resize((224, 224))
    img_npy = np.asarray(image_resize).astype(float) / 128 - 1

    # startTime = 1000 * time.time()
    # img_npy = np.zeros((1024, 1014, 512))

    # Faastlane
    startTime = 1000 * time.time()
    response = {"body": img_npy.tolist()}
    json_data = json.dumps(response)
    img_npy_1 = np.asarray(json.loads(json_data)['body'])
    endTime = 1000 * time.time()
    print("json dumps&&loads use time {}ms".format(endTime - startTime))

    assert img_npy_1.all() == img_npy.all()

    # State-Function
    img_npy_pickle = pickle.dumps(img_npy)

    startTime = 1000 * time.time()
    bucket = df.create_bucket("kingdo", 1024 * 1024 * 5)
    bucket.set("body", img_npy_pickle)
    bucket_get = df.get_bucket("kingdo")
    serialized_img_npy_2 = bucket_get.get("body")
    img_npy_2 = pickle.loads(serialized_img_npy_2)
    endTime = 1000 * time.time()

    print("bucket set&&get use time {}ms".format(endTime - startTime))

    assert img_npy_2.all() == img_npy.all()

    bucket.destroy()
