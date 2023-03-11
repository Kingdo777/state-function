//
// Created by kingdo on 2022/4/2.
//

#ifndef DataFunction_ERRORS_H
#define DataFunction_ERRORS_H

#include <fmt/format.h>
#include <string>
#include <df/utils/macro.h>

namespace df::utils
{
    std::string errors(const std::string& op = "");
}

#endif // DataFunction_ERRORS_H