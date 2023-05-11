import nltk
import pickle
import time
import redis

nltk.data.path.append('nltk_data/')
from nltk.sentiment.vader import SentimentIntensityAnalyzer


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
    transport_start_time = 1000 * time.time()
    redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    body = pickle.loads(redis_client.get("body"))
    transport_end_time = 1000 * time.time()

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

    body_sentiment = pickle.dumps({'sentiment': sentiment,
                                   'reviewType': body['reviewType'] + 0,
                                   'reviewID': (body['reviewID'] + '0')[:-1],
                                   'customerID': (body['customerID'] + '0')[:-1],
                                   'productID': (body['productID'] + '0')[:-1],
                                   'feedback': (body['feedback'] + '0')[:-1]})

    # pass through values
    response = {'statusCode': 200}
    endTime = 1000 * time.time()

    event = timestamp({}, event, startTime, endTime, transport_start_time, transport_end_time)

    transport_start_time = 1000 * time.time()
    redis_client = redis.Redis(host='222.20.94.67', port=6379, db=0)
    redis_client.set("body_sentiment", body_sentiment)
    transport_end_time = 1000 * time.time()

    return timestamp(response, event, startTime, endTime, transport_start_time, transport_end_time)


if __name__ == "__main__":
    print(main({}))
