//
// Created by kingdo on 23-3-6.
//
#include "datafunction-py-interface.h"

extern "C" {
int read_ipc_py(char *addr, size_t len) {
    read_ipc(addr, len);
    return 0;
}

int write_ipc_py(const char *addr, size_t len) {
    write_ipc(std::string(addr, len));
    return 0;
}
}

