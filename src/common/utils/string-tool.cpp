//
// Created by kingdo on 2022/3/10.
//

#include <df/utils/string-tool.h>

bool df::utils::isAllWhitespace(const std::string& input)
{
    return std::all_of(input.begin(), input.end(), isspace);
}

bool df::utils::startsWith(const std::string& input, const std::string& subStr)
{
    if (subStr.empty())
    {
        return false;
    }

    return input.rfind(subStr, 0) == 0;
}

bool df::utils::endsWith(const std::string& value, const std::string& ending)
{
    if (ending.empty() || ending.size() > value.size())
    {
        return false;
    }
    return std::equal(ending.rbegin(), ending.rend(), value.rbegin());
}

bool df::utils::contains(const std::string& input, const std::string& subStr)
{
    if (input.find(subStr) != std::string::npos)
    {
        return true;
    }
    else
    {
        return false;
    }
}

std::string df::utils::removeSubstr(const std::string& input, const std::string& toErase)
{
    std::string output = input;

    size_t pos = output.find(toErase);

    if (pos != std::string::npos)
    {
        output.erase(pos, toErase.length());
    }

    return output;
}

bool df::utils::stringIsInt(const std::string& input)
{
    return !input.empty() && input.find_first_not_of("0123456789") == std::string::npos;
}
