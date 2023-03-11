//
// Created by kingdo on 23-3-6.
//

#ifndef DATAFUNCTION_DATAFUNCTION_PY_INTERFACE_H
#define DATAFUNCTION_DATAFUNCTION_PY_INTERFACE_H

#include <string>
#include <df/shm/shm.h>

extern "C" {
int read_ipc_py(char *addr, size_t len);

int write_ipc_py(const char *addr, size_t len);
}
#endif //DATAFUNCTION_DATAFUNCTION_PY_INTERFACE_H
