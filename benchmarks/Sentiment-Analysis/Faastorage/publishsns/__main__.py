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
    '''
    Sends notification of negative results from sentiment analysis via SNS
    '''

    transport_start_time = 1000 * time.time()
    bucket = df.get_bucket("kingdo-sentiment-analysis")
    body_sentiment = pickle.loads(bucket.get_bytes("body_sentiment"))
    transport_end_time = 1000 * time.time()

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
    bucket.destroy()

    response = {'statusCode': 200}
    endTime = 1000 * time.time()

    time_statistics = timestamp({}, event, startTime, endTime, transport_start_time, transport_end_time)

    response["executeTime"] = "{:.2f} ms".format(time_statistics["executeTime"])
    response["timeStampCost"] = "{:.2f} ms".format(time_statistics["timeStampCost"])
    response["interactionTime"] = "{:.2f} ms".format(time_statistics["interactionTime"])

    return response


if __name__ == "__main__":
    print(main({}))
