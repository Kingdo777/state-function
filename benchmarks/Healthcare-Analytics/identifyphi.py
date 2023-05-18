import json
import pickle

import boto3
import time

from botocore.config import Config
import redis
import datafunction as df

BUCKET = 'kingdo-serverless'
File_KEY = 'faastlane/healthycare/{}'

AWS_ACCESS_KEY_ID = "AKIA2EGUEMCVKZGPBGIC"
AWS_SECRET_KEY_ID = "w9zEt8hTXOkKKbOIc+gWC8FaXfYAkm23b8YhOQ/3"
S3_REGION_NAME = "us-west-2"

global redis_client
global bucket
global s3


def timestamp(response, event,
              start_time,
              execute_time,
              serialize_time,
              init_time,
              transport_time):
    if 'requestTime' in event:
        prior_request_time = event['requestTime'] if 'requestTime' in event else 0
        response['requestTime'] = prior_request_time + start_time - event['endTime']
    else:
        response['requestTime'] = 0

    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_time

    prior_serialize_time = event['serializeTime'] if 'serializeTime' in event else 0
    response['serializeTime'] = prior_serialize_time + serialize_time

    prior_init_time = event['initTime'] if 'initTime' in event else 0
    response['initTime'] = prior_init_time + init_time

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_time

    return response


def extract_entities_from_message(message):
    client = boto3.client(service_name='comprehendmedical',
                          aws_access_key_id="AKIA2EGUEMCVKZGPBGIC",
                          aws_secret_access_key="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",
                          region_name="us-east-1",
                          config=Config(proxies={'https': 'http://222.20.94.67:7890'}))
    return client.detect_phi(Text=message)


def main(event):
    global redis_client, bucket, s3
    op = event["op"]

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.create_bucket("kingdo", 1024 * 40)
    elif op == "FT":
        pass
    else:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_KEY_ID,
                          region_name=S3_REGION_NAME,
                          config=Config(proxies={'https': 'http://192.168.162.239:7890'}))
    init_end_time = 1000 * time.time()

    execute_start_time = 1000 * time.time()
    # Extract the message from the event
    message = event['message']
    # Extract all entities from the message
    response = extract_entities_from_message(message)
    entities_response = {}
    for i in range(2000):
        entities_response["index{}".format(i)] = response['Entities']
    execute_end_time = 1000 * time.time()

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        serialize_entity = json.dumps({"message": event['message'], "entities": entities_response})
    elif op == "OW":
        serialize_entity = pickle.dumps({"message": event['message'], "entities": entities_response})
    else:
        serialize_entity = pickle.dumps(entities_response)
    print(len(serialize_entity) / 1024)
    serialize_end_time = 1000 * time.time()

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set("message", event['message'])
        redis_client.set("entities", serialize_entity)
    elif op == "CB":
        bucket.set("message", event['message'])
        bucket.set("entities", serialize_entity)
    elif op == "FT":
        response["body"] = serialize_entity
    else:
        s3.put_object(Bucket=BUCKET, Key=File_KEY.format("body"), Body=serialize_entity)
    transport_end_time = 1000 * time.time()

    response["endTime"] = 1000 * time.time()
    return timestamp(response, event, 0,
                     execute_end_time - execute_start_time,
                     serialize_end_time - serialize_start_time,
                     init_end_time - init_start_time,
                     transport_end_time - transport_start_time)


if __name__ == "__main__":
    print(main({
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled",
        "op": "OFC"
    }))

    print(main({
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled",
        "op": "OW"
    }))

    result = main({
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled",
        "op": "FT"
    })
    result.pop("body")
    print(result)

    print(main({
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled",
        "op": "CB"
    }))
