//
// Created by 14408 on 2022/2/18.
//

#ifndef StateFunction_CONFIG_H
#define StateFunction_CONFIG_H

#include <chrono>
#include <string>
#include <df/utils/env.h>

namespace df::utils {
    class Config {
    public:
        /// Log
        static std::string LogLevel() { return logLevel; };

        static std::string EnableLogFile() { return enableLogFile; };

        static std::string LogFileBaseDir() { return logFileBaseDir; };


        /// StorageFunctions
        static int SF_NumThreads() { return sfNumThreads; };

        static int SF_NumWorkers() { return sfNumWorkers; };

        static int SF_Cores() { return sfNumWorkers; };

        static int SF_Memory() { return sfNumWorkers; };


        static void print();

    private:
        /// Log
        const static std::string logLevel;
        const static std::string enableLogFile;
        const static std::string logFileBaseDir;

        /// StorageFunctions
        const static int sfNumThreads;
        const static int sfNumWorkers;
        const static int sfCores;
        const static int sfMemory;
    };
}

#endif // StateFunction_CONFIG_H
