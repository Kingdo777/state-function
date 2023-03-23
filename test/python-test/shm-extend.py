import ipc

if __name__ == '__main__':
    shm = ipc.create_shm(0x7777, 4096)
    print(shm.size)
    print(shm.key)
    shm.destroy()
