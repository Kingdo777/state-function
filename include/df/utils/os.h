//
// Created by kingdo on 2022/2/26.
//

#ifndef StateFunction_OS_H
#define StateFunction_OS_H

#include <df/utils/errors.h>
#include <df/utils/macro.h>
#include <df/utils/string-tool.h>

#include <arpa/inet.h>
#include <asm-generic/ioctls.h>
#include <fcntl.h>
#include <grp.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <netdb.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <unordered_map>

namespace df::utils {

    int hardware_concurrency();

    ///################## NetWork ############################
    ///#######################################################

    std::string getIPFromHostname(const std::string &hostname);

    /**
     * Returns the IP for the given interface, or picks one based on
     * an "appropriate" interface name.
     */
    std::string getPrimaryIPForThisHost(const std::string &interface);

    int nonblock_ioctl(int fd, int set);

    int cloexec_ioctl(int fd, int set);

    int nonblock_fcntl(int fd, int set);

    int cloexec_fcntl(int fd, int set);

    int socket_pair(int fds[2]);

    int make_pipe(int fds[2], int flags);

    int kill(pid_t pid, int signum);

    template<typename T>
    ssize_t write_2_fd(int fd, T val) {
        ssize_t n;
        do
            n = ::write(fd, &val, sizeof(T));
        while (n == -1 && errno == EINTR);
        return n;
    }

    template<typename T>
    ssize_t read_from_fd(int fd, T *val) {
        // TODO 应该结合epoll实现timeout机制
        ssize_t n;
        do
            n = ::read(fd, val, sizeof(T));
        while (n == -1 && errno == EINTR);
        return n;
    }

}
#endif // StateFunction_OS_H
