import base64
import json
import os
import statefunction as df
import pickle
import time
import numpy as np
import redis
from PIL import Image

finia = {"body": [
    {
        "body": {
            "marketData": {
                "AMZN": 3185.27,
                "GOOG": 1732.38,
                "MSFT": 221.02
            }
        },
        "duration": 0.00537109375,
        "statusCode": 200,
        "timeStampCost": 0.002685546875,
        "workflowEndTime": 1683509402412.1777,
        "workflowStartTime": 1683509402412.1724
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.383056640625,
        "statusCode": 200,
        "timeStampCost": 0.005615234375,
        "workflowEndTime": 1683509395200.2866,
        "workflowStartTime": 1683509395199.9036
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.3203125,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509390264.0188,
        "workflowStartTime": 1683509390263.6985
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.37353515625,
        "statusCode": 200,
        "timeStampCost": 0.00732421875,
        "workflowEndTime": 1683509384947.9219,
        "workflowStartTime": 1683509384947.5483
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.357177734375,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509375452.846,
        "workflowStartTime": 1683509375452.4888
    }, {
        "body": {
            "marketData": {
                "AMZN": 3185.27,
                "GOOG": 1732.38,
                "MSFT": 221.02
            }
        },
        "duration": 0.00537109375,
        "statusCode": 200,
        "timeStampCost": 0.002685546875,
        "workflowEndTime": 1683509402412.1777,
        "workflowStartTime": 1683509402412.1724
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.383056640625,
        "statusCode": 200,
        "timeStampCost": 0.005615234375,
        "workflowEndTime": 1683509395200.2866,
        "workflowStartTime": 1683509395199.9036
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.3203125,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509390264.0188,
        "workflowStartTime": 1683509390263.6985
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.37353515625,
        "statusCode": 200,
        "timeStampCost": 0.00732421875,
        "workflowEndTime": 1683509384947.9219,
        "workflowStartTime": 1683509384947.5483
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.357177734375,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509375452.846,
        "workflowStartTime": 1683509375452.4888
    }, {
        "body": {
            "marketData": {
                "AMZN": 3185.27,
                "GOOG": 1732.38,
                "MSFT": 221.02
            }
        },
        "duration": 0.00537109375,
        "statusCode": 200,
        "timeStampCost": 0.002685546875,
        "workflowEndTime": 1683509402412.1777,
        "workflowStartTime": 1683509402412.1724
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.383056640625,
        "statusCode": 200,
        "timeStampCost": 0.005615234375,
        "workflowEndTime": 1683509395200.2866,
        "workflowStartTime": 1683509395199.9036
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.3203125,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509390264.0188,
        "workflowStartTime": 1683509390263.6985
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.37353515625,
        "statusCode": 200,
        "timeStampCost": 0.00732421875,
        "workflowEndTime": 1683509384947.9219,
        "workflowStartTime": 1683509384947.5483
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.357177734375,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509375452.846,
        "workflowStartTime": 1683509375452.4888
    }, {
        "body": {
            "marketData": {
                "AMZN": 3185.27,
                "GOOG": 1732.38,
                "MSFT": 221.02
            }
        },
        "duration": 0.00537109375,
        "statusCode": 200,
        "timeStampCost": 0.002685546875,
        "workflowEndTime": 1683509402412.1777,
        "workflowStartTime": 1683509402412.1724
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.383056640625,
        "statusCode": 200,
        "timeStampCost": 0.005615234375,
        "workflowEndTime": 1683509395200.2866,
        "workflowStartTime": 1683509395199.9036
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.3203125,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509390264.0188,
        "workflowStartTime": 1683509390263.6985
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.37353515625,
        "statusCode": 200,
        "timeStampCost": 0.00732421875,
        "workflowEndTime": 1683509384947.9219,
        "workflowStartTime": 1683509384947.5483
    },
    {
        "body": {
            "portfolio": "1234",
            "valid": True
        },
        "duration": 0.357177734375,
        "statusCode": 200,
        "timeStampCost": 0.005859375,
        "workflowEndTime": 1683509375452.846,
        "workflowStartTime": 1683509375452.4888
    },
]}

healthy = [
    {
        "message": "Pt is ## yo woman, ################## with past medical history that includes   - status post cardiac catheterization in ##########.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily, Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled"
    },
    {
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily, Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled",
        "entities": [
            {
                "Id": 0,
                "BeginOffset": 6,
                "EndOffset": 8,
                "Score": 0.9997479319572449,
                "Text": "87",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "AGE",
                "Traits": []
            },
            {
                "Id": 1,
                "BeginOffset": 19,
                "EndOffset": 37,
                "Score": 0.19382844865322113,
                "Text": "highschool teacher",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "PROFESSION",
                "Traits": []
            },
            {
                "Id": 2,
                "BeginOffset": 121,
                "EndOffset": 131,
                "Score": 0.9997519850730896,
                "Text": "April 2019",
                "Category": "PROTECTED_HEALTH_INFORMATION",
                "Type": "DATE",
                "Traits": []
            }
        ]
    },
    {
        "message": "Pt is 87 yo woman, highschool teacher with past medical history that includes   - status post cardiac catheterization in April 2019.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily,             Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled"
    }
]

sentiment = [
    {'statusCode': 200,
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
     'timeStampCost': 0.005859375},
    {'statusCode': 200,
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
     'timeStampCost': 0.002685546875},
    {'statusCode': 200,
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
]

image = Image.open("data/image2.jpg")
img = np.array(image.resize((224, 224))).astype(float) / 128 - 1
ML = img.reshape(1, 224, 224, 3)

if __name__ == '__main__':
    # Redis
    print("for redis, finia size is {}".format(len(pickle.dumps(finia))))
    print("for redis, healthy size is {}".format(len(pickle.dumps(healthy))))
    print("for redis, sentiment size is {}".format(len(pickle.dumps(sentiment))))
    print("for redis, ML size is {}".format(len(pickle.dumps(ML))))

    # Faatanle
    print("for Faatanle, finia size is {}".format(len(json.dumps(finia))))
    print("for Faatanle, healthy size is {}".format(len(json.dumps(healthy))))
    print("for Faatanle, sentiment size is {}".format(len(json.dumps(sentiment))))
    print("for Faatanle, ML size is {}".format(len(json.dumps(ML.tolist()))))
