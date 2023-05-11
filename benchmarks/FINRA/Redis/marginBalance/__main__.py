import json
import pickle
import time

import redis


def agg_timestamp(response, events, execute_start_time, execute_end_time, transport_start_time, transport_end_time):
    stampBegin = 1000 * time.time()
    priorTimeStampCost = 0
    priorExecuteTime = 0
    prior_interaction_time = 0

    for event in events["body"]:
        if 'timeStampCost' in event and event['timeStampCost'] > priorTimeStampCost:
            priorTimeStampCost = event['timeStampCost']
        if 'executeTime' in event and event['executeTime'] > priorExecuteTime:
            priorExecuteTime = event['executeTime']
            prior_interaction_time = event['interactionTime']
            print(event)

    response['executeTime'] = priorExecuteTime + execute_end_time - execute_start_time

    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    response['timeStampCost'] = priorTimeStampCost - (stampBegin - 1000 * time.time())
    return response


def checkMarginBalance(portfolioData, marketData, portfolio):
    marginAccountBalance = json.loads(open('data/marginBalance.json', 'r').read())[portfolio]

    portfolioMarketValue = 0
    for trade in portfolioData:
        security = trade['Security']
        qty = trade['LastQty']
        portfolioMarketValue += qty * marketData[security]

    # Maintenance Margin should be atleast 25% of market value for "long" securities
    # https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210#the-rule
    result = False
    if marginAccountBalance >= 0.25 * portfolioMarketValue:
        result = True

    return result


def main(events):
    transport_start_time = 1000 * time.time()
    actions = ['marketdata', 'trddate', 'volume', 'side', 'lastpx']
    parallel = events['count']
    data = []
    redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    for i in range(1, parallel):
        for action in actions:
            key = "{}_body_{}".format(action, i)
            data.append(pickle.loads(redis_client.get(key)))
    transport_end_time = 1000 * time.time()

    startTime = 1000 * time.time()
    marketData = {}
    validFormat = True
    portfolio = ""

    for body in data:
        if 'marketData' in body:
            marketData = body['marketData']
        elif 'valid' in body:
            portfolio = body['portfolio']
            validFormat = validFormat and body['valid']

    portfolios = json.loads(open('data/portfolios.json', 'r').read())
    portfolioData = portfolios[portfolio]
    marginSatisfied = checkMarginBalance(portfolioData, marketData, portfolio)

    response = {'statusCode': 200,
                'body': {'validFormat': validFormat, 'marginSatisfied': marginSatisfied}}

    endTime = 1000 * time.time()

    time_statistics = agg_timestamp({}, events, startTime, endTime, transport_start_time, transport_end_time)
    response["executeTime"] = "{:.2f} ms".format(time_statistics["executeTime"])
    response["timeStampCost"] = "{:.2f} ms".format(time_statistics["timeStampCost"])
    response["interactionTime"] = "{:.2f} ms".format(time_statistics["interactionTime"])

    return response


if __name__ == '__main__':
    print(main({"body": [
        {
            "body": {
                "marketData": {
                    "AMZN": 3185.27,
                    "GOOG": 1732.38,
                    "MSFT": 221.02
                }
            },
            "duration": 0.00537109375,
            "statusCode": 200,
            "timeStampCost": 0.002685546875,
            "workflowEndTime": 1683509402412.1777,
            "workflowStartTime": 1683509402412.1724
        },
        {
            "body": {
                "portfolio": "1234",
                "valid": True
            },
            "duration": 0.383056640625,
            "statusCode": 200,
            "timeStampCost": 0.005615234375,
            "workflowEndTime": 1683509395200.2866,
            "workflowStartTime": 1683509395199.9036
        },
        {
            "body": {
                "portfolio": "1234",
                "valid": True
            },
            "duration": 0.3203125,
            "statusCode": 200,
            "timeStampCost": 0.005859375,
            "workflowEndTime": 1683509390264.0188,
            "workflowStartTime": 1683509390263.6985
        },
        {
            "body": {
                "portfolio": "1234",
                "valid": True
            },
            "duration": 0.37353515625,
            "statusCode": 200,
            "timeStampCost": 0.00732421875,
            "workflowEndTime": 1683509384947.9219,
            "workflowStartTime": 1683509384947.5483
        },
        {
            "body": {
                "portfolio": "1234",
                "valid": True
            },
            "duration": 0.357177734375,
            "statusCode": 200,
            "timeStampCost": 0.005859375,
            "workflowEndTime": 1683509375452.846,
            "workflowStartTime": 1683509375452.4888
        }
    ]}))
