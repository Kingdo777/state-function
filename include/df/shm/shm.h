//
// Created by kingdo on 23-3-14.
//

#ifndef STATEFUNCTION_SHM_H
#define STATEFUNCTION_SHM_H

#include <df/utils/macro.h>
#include <cstdio>
#include <cstring>
#include <sys/shm.h>


namespace df {
    class SHM {
    public:

        SHM(const SHM &shm) = delete;

        SHM(const SHM &&shm) = delete;

        static std::shared_ptr<SHM> createSHM(key_t key, size_t size);

        static std::shared_ptr<SHM> getSHM(key_t key);

        SHM(key_t key, size_t size);

        explicit SHM(key_t key);

        [[nodiscard]] size_t getSHMSize() const;

        [[nodiscard]] void *getAddress() const;

        void destroy() const {
            DF_CHECK_WITH_EXIT(shmctl(id, IPC_RMID, nullptr) != -1,
                               fmt::format("Delete SHM Stat Wrong: {}", strerror(errno)));
        }

        ~SHM();


    private:

        key_t key;
        size_t size;
        int id;

        void *address;

        struct shmid_ds ipc_info{};

        void updateIPCInfo();

        void reset() {
            DF_CHECK_WITH_EXIT(address != nullptr, "shm is invalid: address is NULL");
            memset(address, 0, size);
        }

    };
}


#endif //STATEFUNCTION_SHM_H
