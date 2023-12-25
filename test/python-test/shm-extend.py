import os

os.environ["STATE_FUNCTION_LOG_LEVEL"] = "off"
if __name__ == '__main__':
    import ipc

    shm = ipc.create_shm(0x7777, 4096)
    print(shm.size)
    print(shm.key)
    shm.destroy()

    ipc.system("ls")
