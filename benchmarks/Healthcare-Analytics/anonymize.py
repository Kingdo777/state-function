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


def mask_entities_in_message(message, entity_list):
    for entity in entity_list:
        message = message.replace(entity['Text'], '#' * len(entity['Text']))
    return message


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


def main(event):
    start_time = 1000 * time.time()
    init_time = 0
    execute_time = 0
    serialize_time = 0
    transport_time = 0

    global redis_client, bucket, s3
    op = event["op"]

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.get_bucket("kingdo")
    elif op == "FT":
        pass
    else:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_KEY_ID,
                          region_name=S3_REGION_NAME,
                          config=Config(proxies={'https': 'http://192.168.162.239:7890'}))
    init_time += 1000 * time.time() - init_start_time

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        message = redis_client.get("message").decode('utf-8')
        entity = redis_client.get("entities")
    elif op == "CB":
        message = bucket.get("message")
        entity = bucket.get_bytes("entities")
    elif op == "FT":
        body = event["body"]
    else:
        body = s3.get_object(Bucket=BUCKET, Key=File_KEY.format("body"))['Body'].read()
    transport_time += 1000 * time.time() - transport_start_time

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        body = json.loads(body)
        message = body["message"]
        entity = body["entities"]["index0"]
    elif op == "OW":
        body = pickle.loads(body)
        message = body["message"]
        entity = body["entities"]["index0"]
    else:
        entity = pickle.loads(entity)["index0"]
    serialize_time += 1000 * time.time() - serialize_start_time

    execute_start_time = 1000 * time.time()
    masked_message = mask_entities_in_message(message, entity)
    execute_time += 1000 * time.time() - execute_start_time

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set("masked_message", masked_message)
    elif op == "CB":
        bucket.set("masked_message", masked_message)
    else:
        response["masked_message"] = masked_message
    transport_time += 1000 * time.time() - transport_start_time

    response["endTime"] = 1000 * time.time()
    print(start_time - event["endTime"])
    return timestamp(response, event,
                     start_time,
                     execute_time,
                     serialize_time,
                     init_time,
                     transport_time)


if __name__ == "__main__":
    data = {'op': 'OW', 'body': {
        'message': 'Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled',
        'entities': {
            "index0": [{'Id': 1, 'BeginOffset': 6, 'EndOffset': 8, 'Score': 0.9997377991676331, 'Text': '87',
                        'Category': 'PROTECTED_HEALTH_INFORMATION', 'Type': 'AGE', 'Traits': []},
                       {'Id': 2, 'BeginOffset': 19, 'EndOffset': 37, 'Score': 0.20220214128494263,
                        'Text': 'highschool teacher', 'Category': 'PROTECTED_HEALTH_INFORMATION', 'Type': 'PROFESSION',
                        'Traits': []},
                       {'Id': 3, 'BeginOffset': 121, 'EndOffset': 131, 'Score': 0.9997790455818176,
                        'Text': 'April 2019',
                        'Category': 'PROTECTED_HEALTH_INFORMATION', 'Type': 'DATE', 'Traits': []}]
        }},
            'endTime': 1683948751044.022, 'requestTime': 0, 'executeTime': 1064.13818359375,
            'serializeTime': 0.005859375, 'initTime': 0.001220703125, 'interactionTime': 0.003662109375}
    print(main(data))

    # data = {'op': 'FT',
    #         'body': '{"message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled", "entities": [{"Id": 1, "BeginOffset": 6, "EndOffset": 8, "Score": 0.9997377991676331, "Text": "87", "Category": "PROTECTED_HEALTH_INFORMATION", "Type": "AGE", "Traits": []}, {"Id": 2, "BeginOffset": 19, "EndOffset": 37, "Score": 0.20220214128494263, "Text": "highschool teacher", "Category": "PROTECTED_HEALTH_INFORMATION", "Type": "PROFESSION", "Traits": []}, {"Id": 3, "BeginOffset": 121, "EndOffset": 131, "Score": 0.9997790455818176, "Text": "April 2019", "Category": "PROTECTED_HEALTH_INFORMATION", "Type": "DATE", "Traits": []}]}'}
    # print(main(data))
    #
    # data = {'op': 'OFC'}
    # print(main(data))
    #
    # data = {'op': 'CB'}
    # print(main(data))
