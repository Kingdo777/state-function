//
// Created by kingdo on 2022/4/2.
//

#ifndef StateFunction_ERRORS_H
#define StateFunction_ERRORS_H

#include <fmt/format.h>
#include <string>
#include <df/utils/macro.h>

namespace df::utils
{
    std::string errors(const std::string& op = "");
}

#endif // StateFunction_ERRORS_H