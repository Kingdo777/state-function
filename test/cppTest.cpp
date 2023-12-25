//
// Created by kingdo on 23-3-18.
//

#include <df/utils/log.h>
#include <string>
#include <utility>
#include <filesystem>
#include "df/utils/json.h"
#include "df/utils/macro.h"

class ClassA {
public:
    std::string name;

    explicit ClassA(std::string name_) : name(std::move(name_)) {}

    ~ClassA() {
        SPDLOG_WARN("~ClassA {}", name);
    }
};

typedef struct {
    std::shared_ptr<ClassA> sp_a;
} StructA;

std::string getExecName() {
    auto currentTime = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::microseconds>(currentTime.time_since_epoch());
    auto microsecond = timestamp.count() % 1000000;

    char buffer[1024];
    auto size = readlink("/proc/self/exe", buffer, sizeof(buffer) - 1);
    auto exec_name = std::filesystem::path(std::string(buffer, size)).filename().string();

    return fmt::format("{}-{}", exec_name, microsecond);
}

int main() {
    SPDLOG_INFO("exec_name: {}", getExecName());
    return 0;

    auto result = R"({"status":"OK","message":{"key":"2004308511","size":""}})";
    df::utils::Json json;
    json.Parse(result);
    if (json.available) {
        auto k = json["message"]["key"].GetString();
        SPDLOG_INFO(k);
    }

    return 0;

//    key_t SHM_KEY =


    auto a1 = (StructA *) malloc(sizeof(StructA));
    a1->sp_a = std::make_shared<ClassA>("Delete a1");
    delete a1;

    auto a2 = (StructA *) malloc(sizeof(StructA));
    a2->sp_a = std::make_shared<ClassA>("Free a2");
    a2->sp_a.reset();
    free(a2);
}