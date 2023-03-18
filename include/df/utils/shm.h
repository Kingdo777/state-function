//
// Created by kingdo on 23-3-14.
//

#ifndef DATAFUNCTION_SHM_H
#define DATAFUNCTION_SHM_H

#include <df/utils/macro.h>
#include <cstdio>
#include <cstring>
#include <sys/shm.h>


namespace df::utils {
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
            if (shmctl(id, IPC_RMID, nullptr) == -1) {
                perror("shmctl failed:");
                DF_CHECK_WITH_EXIT(false, "Delete SHM Stat Wrong");
            }
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


#endif //DATAFUNCTION_SHM_H
