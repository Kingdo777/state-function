import time
from sys import stdout
from sys import stderr
import os, json, traceback
import ipc

env = os.environ


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


def main(event):
    start = time.time() * 1000
    if "op" not in event:
        return {
            "statusCode": "400",
            "body": "must specify op: ping, create, or destroy"
        }

    op = event['op']

    if op == "ping":
        return {
            "statusCode": "200",
            "body": "PONG"
        }

    if op == "create":
        if "key" not in event or "size" not in event:
            return {
                "statusCode": "400",
                "body": "create must specify key&&size"
            }
        key = int(event["key"])
        size = int(event["size"])
        try:
            shm = ipc.create_shm(key, size)
        except Exception as e:
            return {
                "statusCode": "400",
                "body": "create shm failed: {}".format(e)
            }
        return {
            "statusCode": "200",
            "body": "OK",
            "key": key,
            "create_shm_use:": "{:.2f}ms".format(time.time() * 1000 - start)
        }

    if op == "destroy":
        if "key" not in event:
            return {
                "statusCode": "400",
                "body": "destroy must specify key"
            }
        key = event["key"]
        try:
            shm = ipc.get_shm(key)
            shm.destroy()
        except Exception as e:
            return {
                "statusCode": "400",
                "body": "destroy shm failed: {}".format(e)
            }
        return {
            "statusCode": "200",
            "body": "OK",
            "destroy_shm_use:": "{:.2f}ms".format(time.time() * 1000 - start)
        }

    response = {
        "statusCode": "400",
        "body": "Unreachable"
    }
    return response


if __name__ == '__main__':
    try:
        msg = ipc.get_msg(0x7777)
        msg.destroy()
    except:
        pass

    msg = ipc.create_msg(0x7777)
    bucket_key = BucketKey()

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
        else:
            payload["key"] = bucket_key.get(payload["name"])
        res = {}
        try:
            res = main(payload)
        except Exception as ex:
            print(traceback.format_exc(), file=stderr)
            res = {"error": str(ex)}
        print("Sending message: %s" % json.dumps(res))
        if payload["op"] == "destroy" and res["statusCode"] == "200":
            bucket_key.destroy(payload["name"])
        action_msg.send(json.dumps(res))
