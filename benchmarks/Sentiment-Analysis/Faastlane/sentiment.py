import nltk

nltk.data.path.append('nltk_data/')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from utils import *


def main(event):
    startTime = 1000 * time.time()
    sid = SentimentIntensityAnalyzer()
    feedback = event['body']['feedback']
    scores = sid.polarity_scores(feedback)

    if scores['compound'] > 0:
        sentiment = 1
    elif scores['compound'] == 0:
        sentiment = 0
    else:
        sentiment = -1

    # pass through values
    response = {'statusCode': 200,
                'body': {'sentiment': sentiment,
                         'reviewType': event['body']['reviewType'] + 0,
                         'reviewID': (event['body']['reviewID'] + '0')[:-1],
                         'customerID': (event['body']['customerID'] + '0')[:-1],
                         'productID': (event['body']['productID'] + '0')[:-1],
                         'feedback': (event['body']['feedback'] + '0')[:-1]}}

    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == '__main__':
    print(main({'statusCode': 200,
                'body': {'reviewType': 0,
                         'reviewID': '123',
                         'customerID': '456',
                         'productID': '789',
                         'feedback': 'Great product'},
                'duration': 283.23876953125,
                'workflowEndTime': 1683427496102.5159,
                'workflowStartTime': 1683427495819.277,
                'timeStampCost': 0.002685546875}))
