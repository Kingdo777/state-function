import pickle

import boto3
import logging
import time

from botocore.config import Config
import redis


def extract_entities_from_message(message):
    client = boto3.client(service_name='comprehendmedical',
                          aws_access_key_id="AKIA2EGUEMCVKZGPBGIC",
                          aws_secret_access_key="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",
                          region_name="us-east-1",
                          config=Config(proxies={'https': 'http://222.20.94.67:7890'}))
    return client.detect_phi(Text=message)


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
    print('Received message payload. Will extract PII')
    try:
        startTime = 1000 * time.time()
        # Extract the message from the event
        message = event['message']
        # Extract all entities from the message
        entities_response = extract_entities_from_message(message)
        entity = pickle.dumps(entities_response['Entities'])
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
        print('PII entity extraction completed')
        endTime = 1000 * time.time()

        transport_start_time = endTime
        redis_client.set("message", event['message'])
        redis_client.set("entities", entity)
        transport_end_time = 1000 * time.time()

        return timestamp({}, event, startTime, endTime, transport_start_time, transport_end_time)
    except Exception as e:
        logging.error('Exception: %s. Unable to extract PII entities from message' % e)
        raise e


if __name__ == "__main__":
    result = main({
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled"
    })
    print(result)
