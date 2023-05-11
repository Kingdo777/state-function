# import boto3
import time

from utils import timestamp


def main(event):
    '''
    Sends notification of negative results from sentiment analysis via SNS
    '''
    startTime = 1000 * time.time()

    # construct message from input data and publish via SNS
    # sns = boto3.client('sns')
    # sns.publish(
    #    TopicArn = 'arn:aws:sns:XXXXXXXXXXXXXXXX:my-SNS-topic',
    #    Subject = 'Negative Review Received',
    #    Message = 'Review (ID = %i) of %s (ID = %i) received with negative results from sentiment analysis. Feedback from Customer (ID = %i): "%s"' % (int(event['body']['reviewID']),
    #                event['body']['reviewType'], int(event['body']['productID']), int(event['body']['customerID']), event['body']['feedback'])
    # )
    #
    # pass through values

    response = {'statusCode': 200, 'body': event['body']}
    endTime = 1000 * time.time()

    time_statistics = timestamp({}, event, startTime, endTime)

    response["workflowAllTime"] = "{:.2f} ms".format(
        time_statistics["workflowEndTime"] - time_statistics["workflowStartTime"])
    response["executeTime"] = "{:.2f} ms".format(time_statistics["duration"])
    response["timeStampCost"] = "{:.2f} ms".format(time_statistics["timeStampCost"])
    response["interactionTime"] = "{:.2f} ms".format(
        time_statistics["workflowEndTime"] - time_statistics["workflowStartTime"] -
        time_statistics["duration"] -
        time_statistics["timeStampCost"])

    return response
