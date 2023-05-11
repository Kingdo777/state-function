import pickle

import boto3
import logging
import time

from botocore.config import Config
import redis


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
    transport_start_time = 1000 * time.time()
    redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    body_sentiment = pickle.loads(redis_client.get("body_sentiment"))
    transport_end_time = 1000 * time.time()

    startTime = 1000 * time.time()

    dynamodb = boto3.client('dynamodb', aws_access_key_id="AKIAQ4WHHPCKGVH4HO6S",
                            aws_secret_access_key="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",
                            region_name="us-east-1")

    # select correct table based on input data
    if body_sentiment['reviewType'] == 0:
        tableName = 'faastlane-products-table'
    elif body_sentiment['reviewType'] == 1:
        tableName = 'faastlane-services-table'
    else:
        raise Exception("Input review is neither Product nor Service")

    # Not publishing to table to avoid network delays in experiments

    response = {'statusCode': 200}
    endTime = 1000 * time.time()

    return timestamp(response, event, startTime, endTime, transport_start_time, transport_end_time)


if __name__ == "__main__":
    print(main({}))
