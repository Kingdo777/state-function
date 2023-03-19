//
// Created by kingdo on 23-3-14.
//

#include <df/shm/shm.h>

namespace df {
    std::shared_ptr<SHM> df::SHM::createSHM(key_t key, size_t size) {
        auto shm = std::make_shared<SHM>(key, size);
        shm->reset();
        return shm;
    }

    std::shared_ptr<SHM> df::SHM::getSHM(key_t key) {
        return std::make_shared<SHM>(key);
    }

    df::SHM::~SHM() {
        if (-1 == shmdt(address)) {
            perror("shmdt error:");
            DF_CHECK_WITH_EXIT(false, "Detache SHM Wrong");
        }
        SPDLOG_INFO("Destruct SHM object");
    }

    df::SHM::SHM(key_t key_, size_t size_) : key(key_), size(size_), id(0) {
        if ((id = shmget(key, size, 0644 | IPC_CREAT | IPC_EXCL)) < 0) {
            perror("shmget error:");
            DF_CHECK_WITH_EXIT(false, "Create SHM Wrong");
        }
        address = (char *) shmat(id, nullptr, 0);
        if (address == (void *) -1) {
            perror("shmat error:");
            DF_CHECK_WITH_EXIT(false, "Attach SHM Wrong");
        }
        updateIPCInfo();
    }

    df::SHM::SHM(key_t key) : key(key), size(0), id(0) {
        if ((id = shmget(key, 0, 0)) < 0) {
            perror("shmget error:");
            DF_CHECK_WITH_EXIT(false, "Create SHM Wrong");
        }
        address = (char *) shmat(id, nullptr, 0);
        if (address == (void *) -1) {
            perror("shmat error:");
            DF_CHECK_WITH_EXIT(false, "Attach SHM Wrong");
        }

        updateIPCInfo();
        size = ipc_info.shm_segsz;
    }

    void df::SHM::updateIPCInfo() {
        if (shmctl(id, IPC_STAT, &ipc_info) == -1) {
            perror("shmctl failed:");
            DF_CHECK_WITH_EXIT(false, "Get SHM Stat Wrong");
        }
    }

    size_t SHM::getSHMSize() const {
        return size;
    }

    void *SHM::getAddress() const {
        return address;
    }
}