import time
import csv


def timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time):
    stamp_begin = 1000 * time.time()
    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_end_time - execute_start_time
    print(transport_end_time - transport_start_time)

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    prior_cost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = prior_cost - (stamp_begin - 1000 * time.time())
    return response


def main(event):
    startTime = 1000 * time.time()
    with open('data/few_reviews.csv') as csvFile:
        # DictReader -> convert lines of CSV to OrderedDict
        for row in csv.DictReader(csvFile):
            # return just the first loop (row) results!
            body = {}
            for k, v in row.items():
                body[k] = int(v) if k == 'reviewType' else v

    endTime = 1000 * time.time()
    response = {
        'statusCode': 200,
        'body': body,
        "transport_start_time": endTime
    }
    response["end"] = 1000 * time.time()
    print(endTime-startTime)

    return timestamp(response, event, startTime, endTime, 0, 0)


if __name__ == "__main__":
    print(main({}))
