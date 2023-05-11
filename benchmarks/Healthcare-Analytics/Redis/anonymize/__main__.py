import logging
import pickle
import time
import redis


def mask_entities_in_message(message, entity_list):
    for entity in entity_list:
        message = message.replace(entity['Text'], '#' * len(entity['Text']))
    return message


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
    print('Received message payload')
    try:
        transport_start_time = 1000 * time.time()
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
        message = redis_client.get("message").decode('utf-8')
        entity = redis_client.get("entities")
        transport_end_time = 1000 * time.time()

        startTime = 1000 * time.time()
        entity_list = pickle.loads(entity)

        # Mask entities
        masked_message = mask_entities_in_message(message, entity_list)
        endTime = 1000 * time.time()

        event = timestamp({}, event, startTime, endTime, transport_start_time, transport_end_time)

        transport_start_time = endTime
        redis_client.set("message", masked_message)
        transport_end_time = 1000 * time.time()

        return timestamp({}, event, startTime, endTime, transport_start_time, transport_end_time)

    except Exception as e:
        logging.error('Exception: %s. Unable to extract entities from message' % e)
        raise e


if __name__ == "__main__":
    result = main({
        'message': 'Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily, Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled',
        'entities': [{'Id': 0, 'BeginOffset': 6, 'EndOffset': 8, 'Score': 0.9997479319572449, 'Text': '87',
                      'Category': 'PROTECTED_HEALTH_INFORMATION', 'Type': 'AGE', 'Traits': []},
                     {'Id': 1, 'BeginOffset': 19, 'EndOffset': 37, 'Score': 0.19382844865322113,
                      'Text': 'highschool teacher', 'Category': 'PROTECTED_HEALTH_INFORMATION', 'Type': 'PROFESSION',
                      'Traits': []},
                     {'Id': 2, 'BeginOffset': 121, 'EndOffset': 131, 'Score': 0.9997519850730896, 'Text': 'April 2019',
                      'Category': 'PROTECTED_HEALTH_INFORMATION', 'Type': 'DATE', 'Traits': []}]
    })
    print(result)
