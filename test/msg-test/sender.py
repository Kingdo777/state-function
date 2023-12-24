import os

import ipc
import statefunction as sf

Action_Pipe_Key = 0x1111

if __name__ == '__main__':
    try:
        msg = ipc.get_msg(Action_Pipe_Key)
        msg.destroy()
        os.system("ipcrm --shmem-key 0x00010001")
    except Exception as e:
        print(e)
    try:
        msg = ipc.create_msg(Action_Pipe_Key)
        bucket = sf.create_bucket("kingdo", 4096, True, Action_Pipe_Key)
        bucket.set("resize_img", "123")
        print(bucket.get("resize_img"))
        bucket = sf.get_bucket("kingdo", True, Action_Pipe_Key)
        bucket.destroy()
        msg.destroy()
    except Exception as e:
        print(e)
