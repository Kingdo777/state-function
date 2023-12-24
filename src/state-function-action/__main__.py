import time

import ipc


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
    print(main({
        "op": "ping",
    }))

    print(main({
        "op": "create",
        "key": 0x7777,
        "size": "4090"
    }))

    print(main({
        "op": "destroy",
        "key": 0x7777,
    }))
