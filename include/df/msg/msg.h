//
// Created by kingdo on 23-3-14.
//

#ifndef STATEFUNCTION_MSG_H
#define STATEFUNCTION_MSG_H

#include <df/utils/macro.h>
#include <cstdio>
#include <cstring>
#include <sys/msg.h>


namespace df {

    struct msg_buffer {
        __syscall_slong_t msg_type;
        char msg_text[1024];
    };

    class MSG {
    public:

        MSG(const MSG &msg) = delete;

        MSG(const MSG &&msg) = delete;

        explicit MSG(key_t key, bool create = true);

        static std::shared_ptr<MSG> createMSG(key_t key);

        static std::shared_ptr<MSG> getMSG(key_t key);

        void destroy() const;

        [[nodiscard]] std::string receive() const;

        void send(const std::string &msg) const;

    private:
        key_t key;
        int msg_id;

    };
}


#endif //STATEFUNCTION_MSG_H
