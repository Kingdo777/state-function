import logging
import time
from utils import timestamp


def mask_entities_in_message(message, entity_list):
    for entity in entity_list:
        message = message.replace(entity['Text'], '#' * len(entity['Text']))
    return message


def main(event):
    print('Received message payload')
    try:
        startTime = 1000 * time.time()
        # Extract the entities and message from the event
        message = event['message']
        entity_list = event['entities']
        # Mask entities
        masked_message = mask_entities_in_message(message, entity_list)
        endTime = 1000 * time.time()

        response = {
            "message": masked_message,
        }

        return timestamp(response, event, startTime, endTime)

    except Exception as e:
        logging.error('Exception: %s. Unable to extract entities from message' % e)
        raise e
