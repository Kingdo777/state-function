import json
import pickle
import tensorflow as tf
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
    # Use S3 to communicate big messages
    # #####################################################################################################################
    transport_start_time = 1000 * time.time()
    bucket_get = df.get_bucket("kingdo")
    resize_pickle = bucket_get.get_bytes("body")
    transport_end_time = 1000 * time.time()
    # ######################################################################################################################

    # execute function code
    # **********************************************************************************************************************
    execute_start_time = transport_end_time
    img = pickle.loads(resize_pickle)
    gd = tf.compat.v1.GraphDef.FromString(open('data/mobilenet_v2_1.0_224_frozen.pb', 'rb').read())
    inp, predictions = tf.import_graph_def(gd, return_elements=['input:0', 'MobilenetV2/Predictions/Reshape_1:0'])
    with tf.compat.v1.Session(graph=inp.graph):
        x = predictions.eval(feed_dict={inp: img})
    bucket_get.destroy()
    response = {
        "statusCode": 200,
        "body": json.dumps({'predictions': x.tolist()})
    }
    execute_end_time = 1000 * time.time()
    # **********************************************************************************************************************

    response["predictExecuteTime"] = execute_end_time - execute_start_time
    response["resizeExecuteTime"] = event["resizeExecuteTime"]
    return timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time)


if __name__ == '__main__':
    print(main({}))
