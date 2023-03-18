//
// Created by kingdo on 23-3-18.
//

#include <df/utils/log.h>
#include <string>

int main() {
    char data[6] = {'1', '2', '3', '4', '5', '6'};

    auto s1 = std::string{data};
    auto s2 = std::string{data, 6};

    SPDLOG_INFO(s1);
    SPDLOG_INFO(s2);

}