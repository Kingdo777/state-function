import json
import numpy as np
import time
from utils import timestamp


def main(event):
    startTime = 1000 * time.time()
    body = json.loads(event['body'])
    x = np.array(body['predictions'])

    text = "Top 1 Prediction: " + str(x.argmax()) + str(x.max())
    print(text)

    response = {
        "statusCode": 200,
        "body": json.dumps({'render': text})
    }

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


if __name__ == '__main__':
    import predict
    import resize

    print(main(predict.main(resize.main({}))))
