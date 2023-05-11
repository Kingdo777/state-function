import time
import nltk

nltk.data.path.append('nltk_data/')
from nltk.tokenize import word_tokenize
from utils import timestamp


def main(event):
    startTime = 1000 * time.time()
    tokens = word_tokenize(event['message'])

    response = {'statusCode': 200, "body": len(tokens)}
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
