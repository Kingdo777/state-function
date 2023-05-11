import time

import nltk

nltk.data.path.append('nltk_data/')
from nltk.tokenize import word_tokenize


def timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time):
    stamp_begin = 1000 * time.time()
    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_end_time - execute_start_time

    print(transport_end_time - transport_start_time)
    print(execute_end_time - execute_start_time)

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    prior_cost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = prior_cost - (stamp_begin - 1000 * time.time())
    return response


def main(event):
    message = event['message']

    startTime = 1000 * time.time()
    tokens = word_tokenize(message)
    response = {'statusCode': 200, "body": len(tokens)}
    endTime = 1000 * time.time()

    time_statistics = timestamp(response, event, startTime, endTime, event['transport_start_time'], startTime)

    response["executeTime"] = "{:.2f} ms".format(time_statistics["executeTime"])
    response["timeStampCost"] = "{:.2f} ms".format(time_statistics["timeStampCost"])
    response["interactionTime"] = "{:.2f} ms".format(time_statistics["interactionTime"])

    return response


if __name__ == '__main__':
    result = main({
        "message": "Pt is ## yo woman, ################## with past medical history that includes   - status post cardiac catheterization in ##########.She presents today with palpitations and chest pressure.HPI : Sleeping trouble on present dosage of Clonidine. Severe Rash  on face and leg, slightly itchy  Meds : Vyvanse 50 mgs po at breakfast daily, Clonidine 0.2 mgs -- 1 and 1 / 2 tabs po qhs HEENT : Boggy inferior turbinates, No oropharyngeal lesion Lungs : clear Heart : Regular rhythm Skin :  Mild erythematous eruption to hairline Follow-up as scheduled"
    })
    print(result)
