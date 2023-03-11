//
// Created by kingdo on 23-3-6.
//

#ifndef DATA_FUNCTION_SHM_H
#define DATA_FUNCTION_SHM_H

#include <cstdio>
#include <cstring>
#include <sys/ipc.h>
#include <sys/shm.h>

#define MAXBUFSIZE 4096
#define SHAREMEMESIZE 4096
#define SHM_KEY 0x666

int write_ipc(const std::string &content);

int read_ipc(char *addr, size_t len);


#endif //DATA_FUNCTION_SHM_H
