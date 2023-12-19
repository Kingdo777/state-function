//
// Created by kingdo on 23-3-23.
//

#ifndef STATEFUNCTION_NETWORK_H
#define STATEFUNCTION_NETWORK_H

#include <curl/curl.h>
#include <df/utils/log.h>

namespace df::utils {
    // 回调函数，将数据写入字符串
    size_t write_callback(char *ptr, size_t size, size_t nmemb, std::string *userdata);

    std::string POST(const std::string &url, const std::string& body, int timeout);;
}

#endif //STATEFUNCTION_NETWORK_H
