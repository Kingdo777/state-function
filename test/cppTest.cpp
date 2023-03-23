//
// Created by kingdo on 23-3-18.
//

#include <df/utils/log.h>
#include <string>
#include <utility>
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

int main() {

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