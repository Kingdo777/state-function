import time


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
    '''
    Sends notification of negative results from sentiment analysis via SNS
    '''

    body_sentiment = event["body_sentiment"]

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

    response = {'statusCode': 200}
    endTime = 1000 * time.time()

    time_statistics = timestamp({}, event, startTime, endTime, event['transport_start_time'], startTime)

    response["executeTime"] = "{:.2f} ms".format(time_statistics["executeTime"])
    response["timeStampCost"] = "{:.2f} ms".format(time_statistics["timeStampCost"])
    response["interactionTime"] = "{:.2f} ms".format(time_statistics["interactionTime"])
    print(endTime-startTime)
    return response


if __name__ == "__main__":
    print(main({'statusCode': 200,
                'body_sentiment': {
                    'sentiment': 1,
                    'reviewType': 0,
                    'reviewID': '123',
                    'customerID': '456',
                    'productID': '789',
                    'feedback': 'Great product'},
                'transport_start_time': 1683460303476.641,
                'executeTime': 312.311279296875,
                'interactionTime': 62494.548828125,
                'timeStampCost': 0.005859375}
               ))
