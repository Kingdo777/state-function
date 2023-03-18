//
// Created by kingdo on 23-3-13.
//

#ifndef DATAFUNCTION_DATAFUNCTIONKVSTOREBUCKET_H
#define DATAFUNCTION_DATAFUNCTIONKVSTOREBUCKET_H

#include <df/utils/smalloc.h>
#include <df/utils/shm.h>

#include <utility>
#include <set>

namespace df::dataStruct::KV_Store {
    class DataFunctionKVStoreBucket {
    public:

        DataFunctionKVStoreBucket(DataFunctionKVStoreBucket &bucket) = delete;

        DataFunctionKVStoreBucket(DataFunctionKVStoreBucket &&bucket) = delete;

        static std::shared_ptr<DataFunctionKVStoreBucket> CreateBucket(const std::string &name, size_t size) {
            return std::make_shared<DataFunctionKVStoreBucket>(name, size);
        }

        static std::shared_ptr<DataFunctionKVStoreBucket> getBucket(const std::string &name) {
            return std::make_shared<DataFunctionKVStoreBucket>(name);
        }

        DataFunctionKVStoreBucket(std::string name, size_t size) :
                bucket_name(std::move(name)), bucket_size(size) {
            DF_CHECK_WITH_EXIT(bucket_size >= PAGE_SIZE && bucket_size % PAGE_SIZE == 0,
                               "Length must be a multiple of pages.");

            /// TODO remote request DF-Container
            /// DFContainer-Manager allocate key, and create&&send to DF-Container
            key_t SHM_KEY = 0x7777;
            /// DF-Container Create the shm
            auto datafunctionContainer_shm = utils::SHM::createSHM(SHM_KEY, bucket_size);
            //// after create the shm, DFContainer-Manager send the Key to Worker-Container
            /// ################################################################

            /// get shm bey the Key received form DFContainer-Manager
            shm = utils::SHM::getSHM(SHM_KEY);
            bucket_size = shm->getSHMSize();

            /// init KVStoreBucket
            storeMemoryRegion = utils::StaticAllocatableMemory::CreateStaticAllocatableMemory(shm->getAddress(),
                                                                                              shm->getSHMSize());
        }

        explicit DataFunctionKVStoreBucket(std::string name) : bucket_name(std::move(name)), bucket_size(0) {
            /// TODO remote request DF-Container
            /// DFContainer-Manager get the key by name,send to Worker-Container;
            key_t SHM_KEY = 0x7777;
            /// ################################################################

            shm = utils::SHM::getSHM(SHM_KEY);
            bucket_size = shm->getSHMSize();

            storeMemoryRegion = utils::StaticAllocatableMemory::LoadStaticAllocatableMemory(shm->getAddress(),
                                                                                            shm->getSHMSize());
            constructKVStoreValue();
        }

        std::string get(const std::string &key) {
            DF_CHECK_WITH_EXIT(metadata_index_map.contains(key), fmt::format("KEY `{}` is not existed", key));
            auto keys_index = metadata_index_map.at(key);
            char *value_addr = (char *) KVStoreValueVector[keys_index][VALUE_ADDRESS];
            size_t value_size = KVStoreValueVector[keys_index][VALUE_SIZE];
            return std::string{value_addr, value_size};
        }

        uint64_t get(const std::string &key, void **value_addr) {
            DF_CHECK_WITH_EXIT(metadata_index_map.contains(key), fmt::format("KEY `{}` is not existed", key));
            auto keys_index = metadata_index_map.at(key);
            *value_addr = (void *) KVStoreValueVector[keys_index][VALUE_ADDRESS];
            uint64_t value_size = KVStoreValueVector[keys_index][VALUE_SIZE];
            return value_size;
        }

        void set(const char *key, size_t key_size, const char *value, size_t value_size) {
            std::string key_s;
            DF_CHECK_WITH_EXIT(key_s.size() == key_size, "Key must is a string");

            DF_CHECK_WITH_EXIT(!metadata_index_map.contains(key_s), fmt::format("KEY `{}` is existed", key_s));
            metadata_index_map.emplace(key_s, KVStoreValueVector.size());

            char *store_address = static_cast<char *>(storeMemoryRegion->malloc(
                    key_size + value_size + sizeof(size_t) * 2));
            *(size_t *) store_address = key_size;
            memcpy(store_address + sizeof(size_t), key, key_size);
            *(size_t *) (store_address + sizeof(size_t) + key_size) = value_size;
            memcpy(store_address + sizeof(size_t) * 2 + key_size, value, value_size);

            auto value_address = (uint64_t) (store_address + sizeof(size_t) * 2 + key_size);
            KVStoreValueVector.push_back({value_address, value_size});
        }

        void set(const std::string &key, const std::string &value) {
            DF_CHECK_WITH_EXIT(!metadata_index_map.contains(key), fmt::format("KEY `{}` is existed", key));
            metadata_index_map.emplace(key, KVStoreValueVector.size());

            size_t key_size = key.size();
            size_t value_size = value.size();
            char *store_address = static_cast<char *>(storeMemoryRegion->malloc(
                    key_size + value_size + sizeof(size_t) * 2));
            *(size_t *) store_address = key_size;
            memcpy(store_address + sizeof(size_t), key.data(), key_size);
            *(size_t *) (store_address + sizeof(size_t) + key_size) = value_size;
            memcpy(store_address + sizeof(size_t) * 2 + key_size, (void *) value.data(), value_size);


            auto value_address = (uint64_t) (store_address + sizeof(size_t) * 2 + key_size);
            KVStoreValueVector.push_back({value_address, value_size});
        }

        void destroy() {
            /// TODO
            shm->destroy();
        }

    private:
        std::string bucket_name;
        size_t bucket_size;

        enum KVStoreValue_Index {
            VALUE_ADDRESS,
            VALUE_SIZE,
            KVStoreValue_Index_MAX
        };
        std::vector<std::array<uint64_t, KVStoreValue_Index_MAX>> KVStoreValueVector;

        std::unordered_map<std::string, uint64_t> metadata_index_map;


        std::shared_ptr<utils::SHM> shm;
        std::shared_ptr<utils::StaticAllocatableMemory> storeMemoryRegion;

        void constructKVStoreValue() {
            storeMemoryRegion->traverseData([&](const char *address) {
                size_t key_size = *(size_t *) address;
                const char *key_address = address + sizeof(size_t);
                size_t value_size = *(size_t *) (address + sizeof(size_t) + key_size);
                const char *value_address = address + sizeof(size_t) * 2 + key_size;

                metadata_index_map.emplace(std::string(key_address, key_size), KVStoreValueVector.size());
                KVStoreValueVector.push_back({(uint64_t) value_address, value_size});
            });
        }

    };
}


#endif //DATAFUNCTION_DATAFUNCTIONKVSTOREBUCKET_H
