import nltk
import time

nltk.data.path.append('nltk_data/')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


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
    body = event["body"]

    startTime = 1000 * time.time()
    sid = SentimentIntensityAnalyzer()
    feedback = body['feedback']
    scores = sid.polarity_scores(feedback)

    if scores['compound'] > 0:
        sentiment = 1
    elif scores['compound'] == 0:
        sentiment = 0
    else:
        sentiment = -1

    body_sentiment = {'sentiment': sentiment,
                      'reviewType': body['reviewType'] + 0,
                      'reviewID': (body['reviewID'] + '0')[:-1],
                      'customerID': (body['customerID'] + '0')[:-1],
                      'productID': (body['productID'] + '0')[:-1],
                      'feedback': (body['feedback'] + '0')[:-1]}

    # pass through values
    endTime = 1000 * time.time()

    response = {
        'statusCode': 200,
        'body_sentiment': body_sentiment,
        "transport_start_time": endTime
    }
    response["end"] = 1000 * time.time()
    print(endTime-startTime)

    return timestamp(response, event, startTime, endTime, event['transport_start_time'], startTime)


if __name__ == "__main__":
    print(main({'statusCode': 200,
                'body': {
                    'reviewType': 0,
                    'reviewID': '123',
                    'customerID': '456',
                    'productID': '789',
                    'feedback': 'Great product'
                },
                'transport_start_time': 1683460240961.4226,
                'executeTime': 291.6416015625,
                'interactionTime': 0,
                'timeStampCost': 0.002685546875}
               ))
