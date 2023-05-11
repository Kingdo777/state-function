//
// Created by kingdo on 23-3-14.
//
#include <df/utils/config.h>
#include <kvstore/DataFunctionKVStoreBucket.h>
#include <wait.h>

using namespace df::dataStruct::KV_Store;

void write() {
    auto bucket = DataFunctionKVStoreBucket::CreateBucket("kingdo", 40960);
    bucket->set("apple", "12");
    bucket->set("banana", "13");
    bucket->set("mum", "kiss");
    char data[100] = "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol";
    bucket->set("dad", data);
    bucket->set("apple1", "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol");
    bucket->set("banana1", "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol");
    bucket->set("mum1", "fuiwh3n894ctaht894yactnw8ct4oauctolsuytvobsycnsol");

}

void read(bool destroy = false) {
    auto bucket = DataFunctionKVStoreBucket::getBucket("kingdo");
    SPDLOG_INFO(bucket->get("apple"));
    SPDLOG_INFO(bucket->get("banana"));
    SPDLOG_INFO(bucket->get("mum"));
    SPDLOG_INFO(bucket->get("dad"));
    SPDLOG_INFO(bucket->get("apple1"));
    SPDLOG_INFO(bucket->get("banana1"));
    SPDLOG_INFO(bucket->get("mum1"));
    if (destroy)
        bucket->destroy();
}

int create_test() {
    auto start = std::chrono::high_resolution_clock::now();
    write();
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    SPDLOG_INFO("write use : {}ms", duration.count());

    start = std::chrono::high_resolution_clock::now();
    read();
    end = std::chrono::high_resolution_clock::now();
    duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    SPDLOG_INFO("read use : {}ms", duration.count());

    for (int i: {1, 128, 256, 5 * 256, 10 * 256}) {
        int size = i * 4096;
        std::string size_s = fmt::format("{}KB", size / 1024);
        start = std::chrono::high_resolution_clock::now();
        auto bucket = DataFunctionKVStoreBucket::CreateBucket("kingdo", size);
        end = std::chrono::high_resolution_clock::now();
        duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
        SPDLOG_INFO("Create {} use : {}ms", size_s, duration.count());

    }


//    auto bucket = DataFunctionKVStoreBucket::getBucket("kingdo");

    return 0;
}

int main() {
    df::utils::initLog("DataFunctionKVStoreBucketTest");

    create_test();

    return 0;

    write();

    if (fork() == 0) {
        SPDLOG_DEBUG("In Child");
        read();
        return 0;
    }
    wait(nullptr);

    SPDLOG_DEBUG("In Father");
    read(true);
    return 0;
}