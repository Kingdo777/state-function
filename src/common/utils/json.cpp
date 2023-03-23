//
// Created by kingdo on 2022/2/26.
//
#include <df/utils/json.h>

namespace df::utils {

    void Json::Parse(const std::string &str) {
        rapidjson::ParseResult parseResult = Base::Parse(str.c_str());
        if (parseResult && !parseResult.IsError()) {
            available = true;
        }
    }

    std::string Json::serialize() {
        if (available) {
            rapidjson::StringBuffer sb;
            rapidjson::Writer<rapidjson::StringBuffer> writer(sb);
            Base::Accept(writer);
            return sb.GetString();
        } else {
            return "{}";
        }

    }
}