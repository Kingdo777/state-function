//
// Created by kingdo on 2022/2/26.
//

#ifndef DataFunction_JSON_H
#define DataFunction_JSON_H

#include <map>
#include <rapidjson/document.h>
#include <rapidjson/stringbuffer.h>
#include <rapidjson/writer.h>
#include <sstream>
#include <string>
#include <vector>

namespace df::utils {

    class Json : public rapidjson::Document {
        typedef rapidjson::Document Base;
    public:

        bool available = false;

        void Parse(const std::string &str);

        std::string serialize();
    };
}

#endif // DataFunction_JSON_H
