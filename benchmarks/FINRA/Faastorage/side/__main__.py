import json
import pickle
import time
import datafunction as df


def timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time):
    stamp_begin = 1000 * time.time()
    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_end_time - execute_start_time

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    prior_cost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = prior_cost - (stamp_begin - 1000 * time.time())
    return response


def main(event):
    startTime = 1000 * time.time()
    print(event)
    index = event['index']
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

    bucket = df.get_bucket("kingdo-finra")
    body_data = pickle.dumps({'valid': valid, 'portfolio': portfolio})
    response = {'statusCode': 200}
    endTime = 1000 * time.time()

    transport_start_time = endTime
    bucket_ = df.create_bucket("kingdo-finra-side-{}".format(index), 1024 * 4)
    bucket.set("side_body_{}".format(index), body_data)
    transport_end_time = 1000 * time.time()
    bucket_.destroy()

    return timestamp(response, event, startTime, endTime, transport_start_time, transport_end_time)


if __name__ == "__main__":
    print(main({"body": {"portfolio": "1234"}}))
