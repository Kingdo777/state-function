//
// Created by kingdo on 2022/3/4.
//

#ifndef DataFunction_LOCKS_H
#define DataFunction_LOCKS_H

#include <mutex>
#include <shared_mutex>

namespace df::utils
{
    typedef std::unique_lock<std::mutex> UniqueLock; /// 互斥锁
    typedef std::unique_lock<std::recursive_mutex> UniqueRecursiveLock; /// 递归互斥锁
    typedef std::unique_lock<std::shared_mutex> WriteLock; /// 写锁
    typedef std::shared_lock<std::shared_mutex> ReadLock; /// 读锁
}
#endif // DataFunction_LOCKS_H
