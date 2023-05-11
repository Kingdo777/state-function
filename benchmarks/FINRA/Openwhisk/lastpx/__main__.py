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
        px = str(trade['LastPx'])
        if '.' in px:
            a, b = px.split('.')
            if not ((len(a) == 3 and len(b) == 6) or
                    (len(a) == 4 and len(b) == 5) or
                    (len(a) == 5 and len(b) == 4) or
                    (len(a) == 6 and len(b) == 3)):
                print('{}: {}v{}'.format(px, len(a), len(b)))
                valid = False
                break
    response = {'statusCode': 200, 'body': {'valid': valid, 'portfolio': portfolio}}
    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == "__main__":
    print(main({"body": {"portfolio": "1234"}}))
