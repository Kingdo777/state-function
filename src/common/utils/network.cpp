//
// Created by kingdo on 23-3-23.
//

#include <df/utils/network.h>

namespace df::utils {
    size_t write_callback(char *ptr, size_t size, size_t nmemb, std::string *userdata) {
        userdata->append(ptr, size * nmemb);
        return size * nmemb;
    }

    std::string POST(const std::string &url, const std::string& body, int timeout) {
        std::string response;
        CURL *curl = curl_easy_init();
        if (curl) {
            // 设置请求 URL
            curl_easy_setopt(curl, CURLOPT_URL, url.c_str());

            // 设置请求头，指定数据类型为 JSON
            struct curl_slist *headers = nullptr;
            headers = curl_slist_append(headers, "Content-Type: application/json");
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

            // 设置 POST 数据
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());

            // 设置请求 Timeout
            curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout);

            // 设置写回调函数
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

            // 执行请求
            CURLcode res = curl_easy_perform(curl);
            if (res != CURLE_OK) {
                SPDLOG_ERROR("curl_easy_perform() failed: {}", curl_easy_strerror(res));
            }

            // 清理 cURL 句柄和请求头
            curl_easy_cleanup(curl);
            curl_slist_free_all(headers);
        } else {
            SPDLOG_ERROR("curl is null");
        }
        return response;
    }
}