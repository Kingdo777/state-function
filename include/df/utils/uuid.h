//
// Created by kingdo on 2022/3/4.
//

#ifndef StateFunction_UUID_H
#define StateFunction_UUID_H

#include <atomic>
#include <cstdint>
#include <mutex>

#define UUID_LEN 20

namespace df::utils
{
    uint32_t uuid();
    //    uint32_t uuid();
    //    void uuid_reset();
}

#endif // StateFunction_UUID_H
