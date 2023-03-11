//
// Created by kingdo on 23-3-6.
//
#include <string>
#include <df/shm/shm.h>
#include <df/utils/log.h>

int read_ipc(char *addr, size_t len) {
    int shm_id;
    char *shm_p;

    ///  获取共享内存
    if ((shm_id = shmget(SHM_KEY, SHAREMEMESIZE, 0644)) < 0) {
        perror("shmget error:");
        return 1;
    }
    /// 把共享内存链接到当前进程的地址空间
    shm_p = (char *) shmat(shm_id, nullptr, 0);
    if (shm_p == (void *) -1) {
        perror("shmat error:");
        return 1;
    }
    /// 拷贝共享内存中的数据
    memcpy(addr, shm_p, len);

    /// 把共享内存从当前进程分离
    shmdt(shm_p);

    /// 删除共享内存
    if (shmctl(shm_id, IPC_RMID, nullptr) == -1) {
        printf("shmctl failed\n");
        return -1;
    }
    return 0;
}

int write_ipc(const std::string &content) {
    int shm_id;
    char *shm_p;

    /// 获取共享内存，如果不存在则创建
    if ((shm_id = shmget(0x666, SHAREMEMESIZE, 0644 | IPC_CREAT)) < 0) {
        perror("shmget error");
        return 1;
    }

    /// 把共享内存链接到当前进程的地址空间
    shm_p = (char *) shmat(shm_id, nullptr, 0);
    if (shm_p == (void *) -1) {
        perror("shmat error:");
        return 1;
    }

    /// 将数据拷贝到共享内存
    strcpy(shm_p, content.c_str());

    /// 把共享内存从当前进程分离
    shmdt(shm_p);

    return 0;
}
