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
            SPDLOG_ERROR(fmt::format("Detache SHM Wrong: {}", strerror(errno)));
        }
        SPDLOG_DEBUG("Destruct SHM object");
    }

    df::SHM::SHM(key_t key_, size_t size_) : key(key_), size(size_), id(0) {
        DF_CHECK_WITH_EXIT(size >= PAGE_SIZE && size % PAGE_SIZE == 0, "Length must be a multiple of pages.");
        DF_CHECK_WITH_EXIT(!((id = shmget(key, size, 0666 | IPC_CREAT | IPC_EXCL)) < 0),
                           fmt::format("Create SHM Wrong: {}", strerror(errno)));
        address = (char *) shmat(id, nullptr, 0);
        DF_CHECK_WITH_EXIT(address != (void *) -1, fmt::format("Attach SHM Wrong: {}", strerror(errno)));
        updateIPCInfo();
    }

    df::SHM::SHM(key_t key) : key(key), size(0), id(0) {
        DF_CHECK_WITH_EXIT(!((id = shmget(key, 0, 0)) < 0), fmt::format("Get SHM Wrong: {}", strerror(errno)));
        address = (char *) shmat(id, nullptr, 0);
        DF_CHECK_WITH_EXIT(address != (void *) -1, fmt::format("Attach SHM Wrong: {}", strerror(errno)));

        updateIPCInfo();
        size = ipc_info.shm_segsz;
    }

    void df::SHM::updateIPCInfo() {
        DF_CHECK_WITH_EXIT(!(shmctl(id, IPC_STAT, &ipc_info) == -1),
                           fmt::format("Get SHM Stat Wrong: {}", strerror(errno)));
    }

    size_t SHM::getSHMSize() const {
        return size;
    }

    void *SHM::getAddress() const {
        return address;
    }
}