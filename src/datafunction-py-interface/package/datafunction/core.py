import ctypes

# ctypes文档: https://docs.python.org/zh-cn/3.10/library/ctypes.html#module-ctypes

# 我没记错的话, None这个选项是搜索当前进程的加载的所有的库文件,
# 因此 C/CPP 使用cpython的库调用py文件时可以用
# _host_interface = ctypes.CDLL(None)

_host_interface = ctypes.CDLL(
    "/home/kingdo/CLionProjects/DataFunction/cmake-build-debug/out/lib/libdatafunction-py-interface.so")

read_ipc = _host_interface.read_ipc_py
read_ipc.restype = ctypes.c_int
read_ipc.argtypes = [ctypes.c_char_p, ctypes.c_size_t]

write_ipc = _host_interface.write_ipc_py
write_ipc.restype = ctypes.c_int
write_ipc.argtypes = [ctypes.c_char_p, ctypes.c_size_t]


def read_shm() -> str:
    buf = ctypes.create_string_buffer(10)
    read_ipc(buf, 10)
    return buf.value


def write_shm(content: str):
    write_ipc(content.encode(), len(content))


def write_shm_bytes(content: bytes):
    write_ipc(content, len(content))
