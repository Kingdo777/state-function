import json

import time

import boto3
import os
import multiprocessing

from botocore.config import Config

BUCKET = 'kingdo-serverless'
FOLDER = 'faas-workbench/model_training'

AWS_ACCESS_KEY_ID = "AKIA2EGUEMCVKZGPBGIC"
AWS_SECRET_KEY_ID = "w9zEt8hTXOkKKbOIc+gWC8FaXfYAkm23b8YhOQ/3"
S3_REGION_NAME = "us-west-2"


def get_s3_file(key):
    print("get {}".format(key))
    s3_client = boto3.client(service_name='s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_KEY_ID,
                             region_name=S3_REGION_NAME)
    obj = s3_client.get_object(Bucket=BUCKET, Key=key)['Body'].read()


def put_s3_file(file_path, key):
    print("put {}".format(key))
    s3_client = boto3.client(service_name='s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_KEY_ID,
                             region_name=S3_REGION_NAME)
    s3_client.upload_file(file_path, BUCKET, key)


def lambda_handler(event, context):
    index = event['index']

    start = time.time() * 1000

    file_key = os.path.join(FOLDER, "model/lr_model_{}.pk".format(int(100 / index)))

    file_path = "./lr_model_{}.pk".format(int(100 / index))
    put_s3_file(file_path, file_key)

    get_s3_file(file_key)

    print(time.time() * 1000 - start)
    return {
        'statusCode': index,
        'body': json.dumps(time.time() * 1000 - start)
    }


