import json
import time
import json
import pickle

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


def agg_timestamp(response, events,
                  start_time,
                  execute_time,
                  serialize_time,
                  init_time,
                  transport_time):
    prior_execute_time = 0
    prior_serialize_time = 0
    prior_init_time = 0
    prior_interaction_time = 0

    end_Time = 0

    for event in events["body"]:
        if event['endTime'] > end_Time:
            end_Time = event['endTime']
            response['requestTime'] = start_time - event['endTime']
            prior_execute_time = event['executeTime']
            prior_serialize_time = event['serializeTime']
            prior_init_time = event['initTime']
            prior_interaction_time = event['interactionTime']

    response['executeTime'] = prior_execute_time + execute_time
    response['serializeTime'] = prior_serialize_time + serialize_time
    response['initTime'] = prior_init_time + init_time
    response['interactionTime'] = prior_interaction_time + transport_time

    return response


def checkMarginBalance(portfolioData, marketData, portfolio):
    marginAccountBalance = json.loads(open('data/marginBalance.json', 'r').read())[portfolio]

    portfolioMarketValue = 0
    for trade in portfolioData:
        security = trade['Security']
        qty = trade['LastQty']
        portfolioMarketValue += qty * marketData[security]

    # Maintenance Margin should be atleast 25% of market value for "long" securities
    # https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210#the-rule
    result = False
    if marginAccountBalance >= 0.25 * portfolioMarketValue:
        result = True

    return result


def main(events):
    global redis_client, bucket, s3

    start_time = 1000 * time.time()
    init_time = 0
    execute_time = 0
    serialize_time = 0
    transport_time = 0

    op = "FT" if type(events) == list else events["op"]

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.get_bucket("kingdo")
    elif op == "FT":
        pass
    else:
        pass
    init_time += 1000 * time.time() - init_start_time

    transport_start_time = 1000 * time.time()
    actions = ['marketData', 'trddate', 'volume', 'side', 'lastpx']
    data_serialize = []
    if op == "OFC" or op == "CB":
        parallel = events['count']
        for i in range(1, parallel):
            for action in actions:
                key = "{}_{}".format(action, i)
                data_serialize.append(redis_client.get(key) if op == "OFC" else bucket.get_bytes(key))
    elif op == "FT":
        for event in events:
            data_serialize.append(event["body"])
    else:
        for event in events["body"]:
            data_serialize.append(event["body"])
    transport_time += 1000 * time.time() - transport_start_time

    serialize_start_time = 1000 * time.time()
    data = []
    for d in data_serialize:
        if op == "FT":
            d_ = json.loads(d)
            if 'valid' in d_:
                data.append(d_)
            else:
                data.append(d_["marketData"])
        elif op == "OW":
            data.append(d)
        else:
            data.append(pickle.loads(d))
    serialize_time += 1000 * time.time() - serialize_start_time

    # print(data)

    execute_start_time = 1000 * time.time()
    marketData = {}
    validFormat = True
    portfolio = ""
    for body in data:
        if 'valid' in body:
            portfolio = body['portfolio']
            validFormat = validFormat and body['valid']
        else:
            marketData = body

    portfolios = json.loads(open('data/portfolios.json', 'r').read())
    portfolioData = portfolios[portfolio]
    marginSatisfied = checkMarginBalance(portfolioData, marketData, portfolio)
    execute_time += 1000 * time.time() - execute_start_time

    response = {'body': {'validFormat': validFormat, 'marginSatisfied': marginSatisfied}}

    if op == "FT":
        events = {"body": events}

    return agg_timestamp(response, events,
                         start_time,
                         execute_time,
                         serialize_time,
                         init_time,
                         transport_time)


if __name__ == '__main__':
    print(main({'body': [{'endTime': 1684005600844.827, 'executeTime': 1501.5615234375, 'initTime': 0.890869140625,
                          'interactionTime': 0.040283203125, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.027099609375},
                         {'endTime': 1684005599528.6606, 'executeTime': 0.171875, 'initTime': 0.697509765625,
                          'interactionTime': 0.00927734375, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.0068359375},
                         {'endTime': 1684005599517.4524, 'executeTime': 0.268798828125, 'initTime': 0.93212890625,
                          'interactionTime': 0.016357421875, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.0107421875},
                         {'endTime': 1684005599531.8962, 'executeTime': 0.1943359375, 'initTime': 0.732177734375,
                          'interactionTime': 0.01025390625, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.008544921875},
                         {'endTime': 1684005599552.1182, 'executeTime': 0.172607421875, 'initTime': 0.652099609375,
                          'interactionTime': 0.008544921875, 'op': 'CB', 'requestTime': 0, 'serializeTime': 0.0078125},
                         {'endTime': 1684005601050.2285, 'executeTime': 1501.09521484375, 'initTime': 0.7578125,
                          'interactionTime': 0.036376953125, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.026611328125},
                         {'endTime': 1684005599556.5588, 'executeTime': 0.205078125, 'initTime': 0.67431640625,
                          'interactionTime': 0.009765625, 'op': 'CB', 'requestTime': 0, 'serializeTime': 0.0078125},
                         {'endTime': 1684005599543.3481, 'executeTime': 0.1943359375, 'initTime': 0.949951171875,
                          'interactionTime': 0.01171875, 'op': 'CB', 'requestTime': 0, 'serializeTime': 0.007080078125},
                         {'endTime': 1684005599544.889, 'executeTime': 0.156494140625, 'initTime': 0.572509765625,
                          'interactionTime': 0.007568359375, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.00634765625},
                         {'endTime': 1684005599561.4473, 'executeTime': 0.157958984375, 'initTime': 0.653564453125,
                          'interactionTime': 0.009033203125, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.00732421875},
                         {'endTime': 1684005601040.8264, 'executeTime': 1501.562744140625, 'initTime': 0.743408203125,
                          'interactionTime': 0.037109375, 'op': 'CB', 'requestTime': 0, 'serializeTime': 0.02783203125},
                         {'endTime': 1684005599549.281, 'executeTime': 0.194091796875, 'initTime': 0.75244140625,
                          'interactionTime': 0.010009765625, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.00830078125},
                         {'endTime': 1684005599544.8877, 'executeTime': 0.151123046875, 'initTime': 0.59423828125,
                          'interactionTime': 0.00732421875, 'op': 'CB', 'requestTime': 0, 'serializeTime': 0.005859375},
                         {'endTime': 1684005599543.28, 'executeTime': 0.19873046875, 'initTime': 0.81787109375,
                          'interactionTime': 0.010498046875, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.0087890625},
                         {'endTime': 1684005599543.1982, 'executeTime': 0.205322265625, 'initTime': 0.737060546875,
                          'interactionTime': 0.01318359375, 'op': 'CB', 'requestTime': 0,
                          'serializeTime': 0.0087890625}],
                'count': 4,
                'op': 'CB'}))
