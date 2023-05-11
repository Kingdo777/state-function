import json
import time


def agg_timestamp(response, events, startTime, endTime):
    stampBegin = 1000 * time.time()
    priorCost = 0
    workflowStartTime = startTime
    priorEndTime = 0

    for event in events['body']:
        if 'workflowEndTime' in event and event['workflowEndTime'] > priorEndTime:
            priorEndTime = event['workflowEndTime']
            priorCost = event['timeStampCost']
        if 'workflowStartTime' in event and event['workflowStartTime'] < workflowStartTime:
            workflowStartTime = event['workflowStartTime']

    # NOTE: This works only if the parallel step is the first step in the workflow
    prior = priorEndTime - workflowStartTime
    response['duration'] = prior + endTime - startTime
    response['workflowEndTime'] = endTime
    response['workflowStartTime'] = workflowStartTime
    response['memsetTime'] = 0

    # Obscure code, doing to time.time() at the end of fn
    response['timeStampCost'] = priorCost - (stampBegin - 1000 * time.time())
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
    startTime = 1000 * time.time()
    marketData = {}
    validFormat = True
    portfolio = ""

    for event in events['body']:
        body = event['body']
        if 'marketData' in body:
            marketData = body['marketData']
        elif 'valid' in body:
            portfolio = event['body']['portfolio']
            validFormat = validFormat and body['valid']

    portfolios = json.loads(open('data/portfolios.json', 'r').read())
    portfolioData = portfolios[portfolio]
    marginSatisfied = checkMarginBalance(portfolioData, marketData, portfolio)

    response = {'statusCode': 200,
                'body': {'validFormat': validFormat, 'marginSatisfied': marginSatisfied}}

    endTime = 1000 * time.time()

    time_statistics = agg_timestamp({}, events, startTime, endTime)
    response["workflowAllTime"] = "{:.2f} ms".format(
        time_statistics["workflowEndTime"] - time_statistics["workflowStartTime"])
    response["executeTime"] = "{:.2f} ms".format(time_statistics["duration"])
    response["timeStampCost"] = "{:.2f} ms".format(time_statistics["timeStampCost"])
    response["interactionTime"] = "{:.2f} ms".format(
        time_statistics["workflowEndTime"] - time_statistics["workflowStartTime"] -
        time_statistics["duration"] -
        time_statistics["timeStampCost"])
    print(endTime-startTime)
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
