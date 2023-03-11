//
// Created by 14408 on 2022/2/18.
//

#include <df/utils/config.h>
#include <df/utils/log.h>
#include <df/utils/macro.h>
#include <df/utils/os.h>
#include <df/utils/uuid.h>

namespace df::utils {
    const std::string Config::logLevel = getEnvVar("LOG_LEVEL", "trace");
    const std::string Config::enableLogFile = getEnvVar("ENABLE_LOG_FILE", "off");
    const std::string Config::logFileBaseDir = getEnvVar("LOG_FILE_BASE_DIR", "/tmp/df/var/logs/");

    const int Config::sfNumThreads = getIntEnvVar("SF_NUM_THREADS", 1);
    const int Config::sfNumWorkers = getIntEnvVar("SF_NUM_WORKERS", 1);
    const int Config::sfCores = getIntEnvVar("SF_CORES", 1000);
    const int Config::sfMemory = getIntEnvVar("SF_MEMORY", 64);

    void Config::print() {
        SPDLOG_INFO("--- Log ---");
        SPDLOG_INFO("logLevel                       {}", logLevel);
        SPDLOG_INFO("enableLogFile                  {}", enableLogFile);
        SPDLOG_INFO("logFileBaseDir                 {}", logFileBaseDir);

        SPDLOG_INFO("--- Storage Function ---");
        SPDLOG_INFO("sfNumThreads                   {}", sfNumThreads);
        SPDLOG_INFO("sfNumWorkers                   {}", sfNumWorkers);
        SPDLOG_INFO("sfCores                        {}", sfCores);
        SPDLOG_INFO("sfMemory                       {}", sfMemory);

        SPDLOG_INFO("------------------------------------------------------------");
    }
}