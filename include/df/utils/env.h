//
// Created by 14408 on 2022/2/18.
//

#ifndef DataFunction_ENV_H
#define DataFunction_ENV_H

#include <string>

namespace df::utils
{
    void setEnv(std::string const& key, int val, bool overwrite = true);
    void setEnv(std::string const& key, std::string const& val, bool overwrite = true);
    std::string getEnvVar(const std::string& key, const std::string& deflt);
    int getIntEnvVar(const std::string& key, int deflt);
}
#endif // DataFunction_ENV_H
