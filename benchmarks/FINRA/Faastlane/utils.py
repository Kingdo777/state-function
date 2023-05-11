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


def agg_timestamp(response, events, startTime, endTime):
    stampBegin = 1000 * time.time()
    priorCost = 0
    workflowStartTime = startTime
    priorEndTime = 0

    for event in events:
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
