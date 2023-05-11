import json
import time
from utils import *


def main(event):
    startTime = 1000 * time.time()

    portfolio = event['body']['portfolio']
    portfolios = json.loads(open('data/portfolios.json', 'r').read())
    data = portfolios[portfolio]

    valid = True

    for trade in data:
        side = trade['Side']
        # Tag ID: 552, Tag Name: Side, Valid values: 1,2,8
        if not (side == 1 or side == 2 or side == 8):
            valid = False
            break

    response = {'statusCode': 200, 'body': {'valid': valid, 'portfolio': portfolio}}
    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == "__main__":
    print(main({"body": {"portfolio": "1234"}}))
