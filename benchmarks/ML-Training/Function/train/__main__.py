import os

import boto3
from botocore.config import Config

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

import pandas as pd
from time import time
import re
import io

FILE_DIR = '/tmp'
BUCKET = 'kingdo-serverless'
FOLDER = 'faas-workbench/model_training'

AWS_ACCESS_KEY_ID = "AKIA2EGUEMCVKZGPBGIC"
AWS_SECRET_KEY_ID = "w9zEt8hTXOkKKbOIc+gWC8FaXfYAkm23b8YhOQ/3"
S3_REGION_NAME = "us-west-2"

cleanup_re = re.compile('[^a-z]+')
tmp = '/home/kingdo/CLionProjects/DataFunction/benchmarks/ML-Training/Function/model/'


def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence


def main(event):
    dataset_bucket = BUCKET
    index = event['size']
    dataset_object_key = os.path.join(FOLDER, "dataset/reviews10mb.csv")
    model_object_key = os.path.join(FOLDER, "model/lr_model_{}.pk".format(index))

    s3_client = boto3.client(service_name='s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_KEY_ID,
                             region_name=S3_REGION_NAME,
                             config=Config(proxies={'https': 'http://222.20.94.67:7890'}))

    # obj = s3_client.get_object(Bucket=dataset_bucket, Key=dataset_object_key)
    # df = pd.read_csv(io.BytesIO(obj['Body'].read()))

    data_csv = pd.read_csv(
        "/home/kingdo/PycharmProjects/serverless-faas-workbench/dataset/amzn_fine_food_reviews/reviews{}mb.csv".format(
            index))

    start = time()
    data_csv['train'] = data_csv['Text'].apply(cleanup)

    tfidf_vector = TfidfVectorizer(min_df=1).fit(data_csv['train'])

    train = tfidf_vector.transform(data_csv['train'])

    model = LogisticRegression()
    model.fit(train, data_csv['Score'])
    latency = time() - start

    model_file_path = tmp + "lr_model_{}.pk".format(index)
    joblib.dump(model, model_file_path)

    s3_client.upload_file(model_file_path, BUCKET, model_object_key)

    return latency


if __name__ == '__main__':
    sizes = [10, 20, 50, 100]
    latency = []
    for size in sizes:
        latency.append(main({
            "size": size
        }))
    print(latency)
