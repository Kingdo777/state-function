import base64
import json
import os
import datafunction as df
import pickle
import time
import numpy as np
import redis
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


B = 1
KB = 1024 * B
MB = 1024 * KB


def swap_in_out_test():
    # 生成1MB大小的数据
    data = bytearray(int(1.1 * KB))

    # 写入到一个新的文件中
    start_time = time.time()
    with open("test.dat", "wb") as f:
        f.write(data)
    write_time = time.time() - start_time

    # 从文件中读取数据
    start_time = time.time()
    with open("test.dat", "rb") as f:
        read_data = f.read()
    read_time = time.time() - start_time

    # 删除测试文件
    os.remove("test.dat")

    # 打印结果
    print(f"write: {write_time * 1000:.5f} ms")
    print(f"read: {read_time * 1000:.5f} ms")


def data_access_test():
    sizes_ = ["512B", "1KB", "4KB", "512KB", "1MB", "5MB", "10MB"]
    sizes = [(1, 1, 512), (1, 1, 1024), (1, 4, 1024), (1, 512, 1024), (1, 1024, 1024), (5, 1024, 1024),
             (10, 1024, 1024)]
    # sizes = [(1, 1, 512)]

    i = 0
    for size in sizes:
        data = np.zeros(size)
        # data_size = (int(data.size / 1024) + 4) * 1024
        # print(data_size)
        # continue

        # Faastlane
        # startTime = 1000 * time.time()
        # response = {"body": data.tolist()}
        # json_data = json.dumps(response)
        # data1 = np.asarray(json.loads(json_data)['body'])
        # endTime = 1000 * time.time()
        # print("Faastlane  transfer {} use {} ms".format(sizes_[i], endTime - startTime))
        #

        data_dumps_start = 1000 * time.time()
        data_pickle = pickle.dumps(data)
        data_size = (int(len(data_pickle) / 1024) + 4) * 1024
        data_dumps_end = 1000 * time.time()

        print("dumps {}KB data use: ".format(len(data_pickle) / 1024,))

        # Faastorage
        startTime = 1000 * time.time()
        bucket = df.create_bucket("kingdo", data_size)
        endTime = 1000 * time.time()
        bucket.set("body", pickle.dumps(data))
        data2 = pickle.loads(bucket.get_bytes("body"))
        endTime_2 = 1000 * time.time()
        bucket.destroy()
        print("Faastorage Create SHM {} use {} ms, read use {} ms".format(sizes_[i], endTime - startTime,
                                                                          endTime_2 - endTime))

        # Redis
        startTime = 1000 * time.time()
        client = redis.Redis(host='222.20.94.67', port=6379, db=0, )
        d = pickle.dumps(data)
        endTime1 = 1000 * time.time()

        client.set("body", d)
        d_ = client.get("body")
        endTime2 = 1000 * time.time()

        data_3 = pickle.loads(d_)
        endTime3 = 1000 * time.time()
        print("Redis   transfer {} use {} ms,c use ".format(endTime2 - endTime1,
                                                            endTime1 - startTime + endTime3 - endTime2))

        i = i + 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # swap_in_out_test()

    data_access_test()

    # read_write_test()

    # image = Image.open("data/image2.jpg")
    # img = np.array(image.resize((224, 224))).astype(float) / 128 - 1
    # img_npy = img.reshape(1, 224, 224, 3)

    # startTime = 1000 * time.time()
    # img_npy = np.zeros((1024, 1014, 10))

    # Faastlane
    # startTime = 1000 * time.time()
    # response = {"body": img_npy.tolist()}
    # json_data = json.dumps(response)
    # img_npy_1 = np.asarray(json.loads(json_data)['body'])
    # endTime = 1000 * time.time()
    # print("json dumps&&loads use time {}ms".format(endTime - startTime))
    # assert img_npy_1.all() == img_npy.all()

    # Data-Function
    # img_npy_pickle = pickle.dumps(img_npy)
    # bucket = df.create_bucket("kingdo", (int(len(img_npy_pickle) / 1024 / 1024) + 1) * 1024 * 1024)
    # startTime = 1000 * time.time()
    # bucket.set("body", img_npy_pickle)
    # bucket_get = df.get_bucket("kingdo")
    # serialized_img_npy_2 = bucket_get.get_bytes("body")
    # endTime = 1000 * time.time()
    # img_npy_2 = pickle.loads(serialized_img_npy_2)
    # print("bucket set&&get use time {}ms".format(endTime - startTime))
    # assert img_npy_2.all() == img_npy.all()
    # bucket.destroy()

    # Redis
    # img_npy_pickle = pickle.dumps(img_npy)
    # redis_set_client = redis.Redis(host='222.20.94.67', port=6379, db=0, )
    # startTime = 1000 * time.time()
    # redis_set_client.set("body", img_npy_pickle)
    # redis_get_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    # serialized_img_npy_3 = redis_get_client.get("body")
    # endTime = 1000 * time.time()
    # img_npy_3 = pickle.loads(serialized_img_npy_3)
    # print("redis set&&get use time {}ms".format(endTime - startTime))
    # assert img_npy_3.all() == img_npy.all()
