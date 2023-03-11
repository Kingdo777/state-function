//
// Created by kingdo on 2022/3/10.
//

#ifndef DataFunction_STRING_TOOL_H
#define DataFunction_STRING_TOOL_H

#include <algorithm>
#include <memory>
#include <stdexcept>
#include <string>

namespace df::utils
{

    bool isAllWhitespace(const std::string& input);

    bool startsWith(const std::string& input, const std::string& subStr);

    bool endsWith(std::string const& value, std::string const& ending);

    bool contains(const std::string& input, const std::string& subStr);

    std::string removeSubstr(const std::string& input, const std::string& toErase);

    bool stringIsInt(const std::string& input);
}

#endif //DataFunction_STRING_TOOL_H
