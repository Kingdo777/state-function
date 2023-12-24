//
// Created by kingdo on 23-3-13.
//

#ifndef STATEFUNCTION_STATEFUNCTIONKVSTOREBUCKET_H
#define STATEFUNCTION_STATEFUNCTIONKVSTOREBUCKET_H

#include <df/smalloc/smalloc.h>
#include <df/shm/shm.h>
#include <df/msg/msg.h>
#include <df/utils/network.h>
#include <df/utils/json.h>

#include <utility>
#include <set>
#include <sys/ipc.h>
#include <sys/msg.h>

#define STATE_FUNCTION_PIPE_KEY 0x7777

namespace df::dataStruct::KV_Store {
    class StateFunctionKVStoreBucket {
    public:

        StateFunctionKVStoreBucket(StateFunctionKVStoreBucket &bucket) = delete;

        StateFunctionKVStoreBucket(StateFunctionKVStoreBucket &&bucket) = delete;

        static std::shared_ptr<StateFunctionKVStoreBucket>
        CreateBucket(const std::string &name, size_t size, bool use_pipe = false,
                     key_t self_pipe_key = -1) {
            return std::make_shared<StateFunctionKVStoreBucket>(name, size, use_pipe, self_pipe_key);
        }

        static std::shared_ptr<StateFunctionKVStoreBucket>
        GetBucket(const std::string &name, bool use_pipe = false, key_t self_pipe_key = -1) {
            return std::make_shared<StateFunctionKVStoreBucket>(name, use_pipe, self_pipe_key);
        }

        StateFunctionKVStoreBucket(std::string name, size_t size, bool use_pipe = false,
                                   key_t self_pipe_key = -1) :
                bucket_name(std::move(name)), bucket_size(size), use_pipe(use_pipe), self_pipe_key(self_pipe_key) {
            DF_CHECK_WITH_EXIT(bucket_size >= PAGE_SIZE && bucket_size % PAGE_SIZE == 0,
                               "Length must be a multiple of pages.");

            key_t SHM_KEY;
            if (use_pipe) {
                auto result = post_by_pipe(fmt::format(
                        R"({{"action_pipe_key":{},"op":"{}","name":"{}","size":{}}})",
                        self_pipe_key, "create", bucket_name, size), self_pipe_key);
                SPDLOG_INFO("create result by pipe: {}", result);
                df::utils::Json json;
                json.Parse(result);
                DF_CHECK_WITH_EXIT(json.available, "post_by_pipe to create shm, the result is not a JSON object");
                DF_CHECK_WITH_EXIT(json.HasMember("statusCode") && json.HasMember("body") &&
                                   json["statusCode"].IsString() && json["body"].IsString() &&
                                   json["statusCode"] == "200" && json["body"] == "OK",
                                   "post_by_pipe to create shm, the result statusCode or body is undefined");
                DF_CHECK_WITH_EXIT(json.HasMember("key") && json["key"].IsInt(),
                                   "post_by_pipe to create shm, the result key is not find or not a int");
                SHM_KEY = json["key"].GetInt();
            } else {
                auto result = utils::POST("http://222.20.94.67:7070/create",
                                          fmt::format(R"({{"name":"{}","size":"{}"}})", bucket_name, size), 60);
                SPDLOG_INFO(result);
                df::utils::Json json;
                json.Parse(result);
                DF_CHECK_WITH_EXIT(json.available, "POST to create shm, the result is not a JSON object");
                DF_CHECK_WITH_EXIT(json.HasMember("status") && json["status"].IsString(),
                                   "POST to create shm, the result status is undefined");
                DF_CHECK_WITH_EXIT(json.HasMember("message"),
                                   "POST to create shm, the result message is undefined");
                DF_CHECK_WITH_EXIT(json["status"] == "OK",
                                   fmt::format("POST to create shm, the result status is Error, {}",
                                               json["message"].GetString()));
                DF_CHECK_WITH_EXIT(json["message"].IsObject(),
                                   "POST to create shm, the result message is not a Object");

                SHM_KEY = key_t(strtol(json["message"]["key"].GetString(), nullptr, 10));
            }

            /// get shm bey the Key received form DFContainer-Manager
            shm = SHM::getSHM(SHM_KEY);
            bucket_size = shm->getSHMSize();

            /// init KVStoreBucket
            storeMemoryRegion = StaticAllocatableMemory::CreateStaticAllocatableMemory(shm->getAddress(),
                                                                                       shm->getSHMSize());
        }

        explicit StateFunctionKVStoreBucket(std::string name, bool use_pipe = false,
                                            key_t self_pipe_key = -1) :
                bucket_name(std::move(name)), bucket_size(0), use_pipe(use_pipe), self_pipe_key(self_pipe_key) {
            key_t SHM_KEY;
            if (use_pipe) {
                auto result = post_by_pipe(fmt::format(
                        R"({{"action_pipe_key":{},"op":"{}","name":"{}"}})",
                        self_pipe_key, "get", bucket_name), self_pipe_key);
                SPDLOG_INFO("get result by pipe: {}", result);
                df::utils::Json json;
                json.Parse(result);
                DF_CHECK_WITH_EXIT(json.available, "post_by_pipe to get shm, the result is not a JSON object");
                DF_CHECK_WITH_EXIT(json.HasMember("statusCode") && json.HasMember("body") &&
                                   json["statusCode"].IsString() && json["body"].IsString() &&
                                   json["statusCode"] == "200" && json["body"] == "OK",
                                   "post_by_pipe to get shm, the result statusCode or body is undefined");
                DF_CHECK_WITH_EXIT(json.HasMember("key") && json["key"].IsInt(),
                                   "post_by_pipe to create shm, the result key is not find or not a int");
                SHM_KEY = json["key"].GetInt();
            } else {
                auto result = utils::POST("http://222.20.94.67:7070/get",
                                          fmt::format(R"({{"name":"{}"}})", bucket_name), 60);
                df::utils::Json json;
                json.Parse(result);
                DF_CHECK_WITH_EXIT(json.available, "POST to get shm, the result is not a JSON object");
                DF_CHECK_WITH_EXIT(json.HasMember("status") && json["status"].IsString(),
                                   "POST to get shm, the result status is undefined");
                DF_CHECK_WITH_EXIT(json.HasMember("message"),
                                   "POST to get shm, the result message is undefined");
                DF_CHECK_WITH_EXIT(json["status"] == "OK",
                                   fmt::format("POST to get shm, the result status is Error, {}",
                                               json["message"].GetString()));
                DF_CHECK_WITH_EXIT(json["message"].IsObject(), "POST to get shm, the result message is not a Object");

                SHM_KEY = key_t(strtol(json["message"]["key"].GetString(), nullptr, 10));
            }
            shm = SHM::getSHM(SHM_KEY);
            bucket_size = shm->getSHMSize();

            storeMemoryRegion = StaticAllocatableMemory::LoadStaticAllocatableMemory(shm->getAddress(),
                                                                                     shm->getSHMSize());
            constructKVStoreValue();
        }

        std::string get(const std::string &key) {
            DF_CHECK_WITH_EXIT(!destroyed, "Bucket has been destroyed");
            DF_CHECK_WITH_EXIT(metadata_index_map.contains(key), fmt::format("KEY `{}` is not existed", key));
            auto keys_index = metadata_index_map.at(key);
            char *value_addr = (char *) KVStoreValueVector[keys_index][VALUE_ADDRESS];
            size_t value_size = KVStoreValueVector[keys_index][VALUE_SIZE];
            return std::string{value_addr, value_size};
        }

        uint64_t get(const std::string &key, void **value_addr) {
            DF_CHECK_WITH_EXIT(!destroyed, "Bucket has been destroyed");
            DF_CHECK_WITH_EXIT(metadata_index_map.contains(key), fmt::format("KEY `{}` is not existed", key));
            auto keys_index = metadata_index_map.at(key);
            *value_addr = (void *) KVStoreValueVector[keys_index][VALUE_ADDRESS];
            uint64_t value_size = KVStoreValueVector[keys_index][VALUE_SIZE];
            return value_size;
        }

        void set(const char *key, size_t key_size, const char *value, size_t value_size) {
            DF_CHECK_WITH_EXIT(!destroyed, "Bucket has been destroyed");
            std::string key_s{key, key_size};
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
            DF_CHECK_WITH_EXIT(!destroyed, "Bucket has been destroyed");
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

        size_t getBucketSize() const {
            return bucket_size;
        }

        void destroy() {
            if (use_pipe) {
                auto result = post_by_pipe(fmt::format(
                        R"({{"action_pipe_key":{},"op":"{}","name":"{}"}})",
                        self_pipe_key, "destroy", bucket_name), self_pipe_key);
                SPDLOG_INFO("destroy result by pipe: {}", result);
                df::utils::Json json;
                json.Parse(result);
                DF_CHECK_WITH_EXIT(json.available, "post_by_pipe to destroy shm, the result is not a JSON object");
                DF_CHECK_WITH_EXIT(json.HasMember("statusCode") && json.HasMember("body") &&
                                   json["statusCode"].IsString() && json["body"].IsString() &&
                                   json["statusCode"] == "200" && json["body"] == "OK",
                                   "post_by_pipe to destroy shm, the result statusCode or body is undefined");
            } else {
                auto result = utils::POST("http://222.20.94.67:7070/destroy",
                                          fmt::format(R"({{"name":"{}"}})", bucket_name), 60);
                df::utils::Json json;
                json.Parse(result);
                DF_CHECK_WITH_EXIT(json.available, "POST to destroySHM, the result is not a JSON object");
                DF_CHECK_WITH_EXIT(json.HasMember("status") && json["status"].IsString(),
                                   "POST to destroySHM, the result status is undefined");
                DF_CHECK_WITH_EXIT(json.HasMember("message"),
                                   "POST to destroySHM, the result message is undefined");
                DF_CHECK_WITH_EXIT(json["status"] == "OK",
                                   fmt::format("POST to destroySHM, the result status is Error, {}",
                                               json["message"].GetString()));
                DF_CHECK_WITH_EXIT(json["message"].IsString(),
                                   "POST to destroySHM, the result message is not a Object");
            }
            destroyed = true;
        }

    private:
        std::string bucket_name;
        size_t bucket_size;
        bool use_pipe = false;
        key_t self_pipe_key;

        bool destroyed = false;

        enum KVStoreValue_Index {
            VALUE_ADDRESS,
            VALUE_SIZE,
            KVStoreValue_Index_MAX
        };
        std::vector<std::array<uint64_t, KVStoreValue_Index_MAX>> KVStoreValueVector;

        std::unordered_map<std::string, uint64_t> metadata_index_map;


        std::shared_ptr<SHM> shm;
        std::shared_ptr<StaticAllocatableMemory> storeMemoryRegion;

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

        static std::string post_by_pipe(const std::string &data, key_t self_pipe_key) {
            key_t msgid = msgget(STATE_FUNCTION_PIPE_KEY, 0666);
            DF_CHECK_WITH_EXIT(msgid != -1, fmt::format("get msg queue failed: {}", strerror(errno)));
            msg_buffer msg{};
            msg.msg_type = 1;
            strcpy(msg.msg_text, data.c_str());
            DF_CHECK_WITH_EXIT(msgsnd(msgid, &msg, sizeof(msg.msg_text), 0) != -1,
                               fmt::format("send msg failed: {}", strerror(errno)));

            key_t self_msgid = msgget(self_pipe_key, 0666);
            DF_CHECK_WITH_EXIT(self_msgid != -1, fmt::format("get msg queue failed: {}", strerror(errno)));
            msg_buffer self_msg{};
            DF_CHECK_WITH_EXIT(msgrcv(self_msgid, &self_msg, sizeof(self_msg.msg_text), 1, 0) != -1,
                               fmt::format("receive msg failed: {}", strerror(errno)));
            return self_msg.msg_text;
        }

    };
}


#endif //STATEFUNCTION_STATEFUNCTIONKVSTOREBUCKET_H
