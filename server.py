import json

from action import main as main

import ipc


class BucketKey:
    def __init__(self):
        self.key = 0
        self.bucket_name_2_key_map = dict()

    def gen(self, name):
        if name in self.bucket_name_2_key_map:
            return None
        else:
            self.key = (self.key + 1) % 0x10000
            self.bucket_name_2_key_map[name] = self.key + 0x10000
            return self.bucket_name_2_key_map[name]

    def get(self, name):
        if name in self.bucket_name_2_key_map:
            return self.bucket_name_2_key_map[name]
        else:
            return None

    def destroy(self, name):
        if name in self.bucket_name_2_key_map:
            del self.bucket_name_2_key_map[name]


def run_state_function():
    msg = ipc.create_msg(0x7777)
    bucket_key = BucketKey()

    # for handling the request from the pipe
    while True:
        print("Waiting for message!!!!!")
        data = msg.receive()
        print("Received message: %s" % data)
        if data == "exit": break
        payload = json.loads(data)
        action_pipe_key = payload["action_pipe_key"]
        action_msg = ipc.get_msg(action_pipe_key)
        if payload["op"] == "get":
            key = bucket_key.get(payload["name"])
            if key is None:
                action_msg.send(json.dumps({
                    "statusCode": "400",
                    "body": "bucket not exist"
                }))
            else:
                action_msg.send(json.dumps({
                    "statusCode": "200",
                    "body": "OK",
                    "key": key
                }))
            continue
        if payload["op"] == "create":
            payload["key"] = bucket_key.gen(payload["name"])
            if payload["key"] is None:
                action_msg.send(json.dumps({
                    "statusCode": "400",
                    "body": "bucket `{}` already exist".format(payload["name"])
                }))
                continue
        else:
            payload["key"] = bucket_key.get(payload["name"])
            if payload["key"] is None:
                action_msg.send(json.dumps({
                    "statusCode": "400",
                    "body": "bucket `{}` not exist".format(payload["name"])
                }))
                continue
        res = {}

        try:
            res = main(payload)
        except Exception as ex:
            res = {"error": str(ex)}
        print("Sending message: %s" % json.dumps(res))
        if payload["op"] == "destroy" and res["statusCode"] == "200":
            bucket_key.destroy(payload["name"])
        action_msg.send(json.dumps(res))


if __name__ == "__main__":
    run_state_function()
