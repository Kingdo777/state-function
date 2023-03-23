import ipc


def main(event):
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
        shm = ipc.create_shm(key, size)
        return {
            "statusCode": "200",
            "body": "OK"
        }

    if op == "destroy":
        if "key" not in event:
            return {
                "statusCode": "400",
                "body": "destroy must specify key"
            }
        key = event["key"]
        shm = ipc.get_shm(key)
        shm.destroy()
        return {
            "statusCode": "200",
            "body": "OK"
        }

    response = {
        "statusCode": "200",
        "body": "Success"
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
