import json
import time


def timestamp(response, event, startTime, endTime):
    stampBegin = 1000 * time.time()
    prior = event['body']['duration'] if 'duration' in event else 0
    response['duration'] = prior + endTime - startTime
    response['workflowEndTime'] = endTime
    response['workflowStartTime'] = event['body']['workflowStartTime'] if 'workflowStartTime' in event else startTime
    priorCost = event['body']['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = priorCost - (stampBegin - 1000 * time.time())
    return response


def main(event):
    startTime = 1000 * time.time()

    portfolio = event['body']['portfolio']
    portfolios = json.loads(open('data/portfolios.json', 'r').read())
    data = portfolios[portfolio]

    valid = True

    for trade in data:
        qty = str(trade['LastQty'])
        # Tag ID: 32, Tag Name: LastQty, Format: max 8 characters, no decimal
        if (len(qty) > 8) or ('.' in qty):
            valid = False
            break

    response = {'statusCode': 200, 'body': {'valid': valid, 'portfolio': portfolio}}
    print(response)
    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == "__main__":
    print(main({"body": {"portfolio": "1234"}}))
