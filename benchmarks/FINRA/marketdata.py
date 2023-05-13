import json
import pickle
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
    global redis_client, bucket, s3
    op = event["op"]
    if op != "FT":
        index = event["index"]

    init_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    elif op == "CB":
        bucket = df.get_bucket("kingdo")
    elif op == "FT":
        pass
    else:
        pass
    init_end_time = 1000 * time.time()

    execute_start_time = 1000 * time.time()
    portfolioType = event['body']['portfolioType']
    tickersForPortfolioTypes = {'S&P': ['GOOG', 'AMZN', 'MSFT']}
    tickers = tickersForPortfolioTypes[portfolioType]
    prices = {}
    # for ticker in tickers:
    #     # Get last closing price
    #
    #     ####### this get an 403
    #     # tickerObj = yf.Ticker(ticker)
    #     # data = tickerObj.history(period="1d", proxy="http://127.0.0.1:7890")
    #     # price = data['Close'].unique()[0]
    #
    #     ###### let us get it by hand
    #     data = requests.get(
    #         url="https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1&interval=1d&includePrePost=False&events=div%2Csplits".
    #         format(ticker),
    #         proxies={"https": "http://222.20.68.145:7890"},
    #         headers={
    #             'User-Agent': 'Mozilla/5.0'
    #         }
    #     ).json()
    #     price = data['chart']['result'][0]['indicators']['quote'][0]['close'][0]
    #
    #     prices[ticker] = price
    time.sleep(1.5)
    prices = {'GOOG': 1732.38, 'AMZN': 3185.27, 'MSFT': 221.02}
    execute_end_time = 1000 * time.time()

    serialize_start_time = 1000 * time.time()
    if op == "FT":
        serialize_data = json.dumps({'marketData': prices})
    elif op == "OW":
        serialize_data = prices
    else:
        serialize_data = pickle.dumps(prices)
    serialize_end_time = 1000 * time.time()

    response = {
        "op": event["op"]
    }

    transport_start_time = 1000 * time.time()
    if op == "OFC":
        redis_client.set('marketData_{}'.format(index), serialize_data)
    elif op == "CB":
        bucket.set('marketData_{}'.format(index), serialize_data)
    elif op == "FT":
        response["body"] = serialize_data
    else:
        response["body"] = serialize_data
    transport_end_time = 1000 * time.time()

    response["endTime"] = 1000 * time.time()
    return timestamp(response, event, 0,
                     execute_end_time - execute_start_time,
                     serialize_end_time - serialize_start_time,
                     init_end_time - init_start_time,
                     transport_end_time - transport_start_time)


if __name__ == "__main__":
    print(main({'body': {'portfolioType': 'S&P'}}))
