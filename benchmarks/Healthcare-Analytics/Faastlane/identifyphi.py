import boto3
import logging
import time

from botocore.config import Config
from utils import timestamp


def extract_entities_from_message(message):
    client = boto3.client(service_name='comprehendmedical',
                          aws_access_key_id="AKIA2EGUEMCVKZGPBGIC",
                          aws_secret_access_key="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",
                          region_name="us-east-1",
                          config=Config(proxies={'https': 'http://222.20.94.67:7890'}))
    return client.detect_phi(Text=message)


def main(event):
    print('Received message payload. Will extract PII')
    try:
        startTime = 1000 * time.time()
        # Extract the message from the event
        message = event['message']
        # Extract all entities from the message
        entities_response = extract_entities_from_message(message)
        entity_list = entities_response['Entities']
        print('PII entity extraction completed')
        endTime = 1000 * time.time()

        response = {
            "message": event['message'],
            "entities": entity_list,
        }

        return timestamp(response, event, startTime, endTime)
    except Exception as e:
        logging.error('Exception: %s. Unable to extract PII entities from message' % e)
        raise e
