//
// Created by kingdo on 23-3-14.
//

#include <df/msg/msg.h>

namespace df {
    std::shared_ptr<MSG> df::MSG::createMSG(key_t key) {
        auto msg = std::make_shared<MSG>(key, true);
        return msg;
    }

    std::shared_ptr<MSG> df::MSG::getMSG(key_t key) {
        return std::make_shared<MSG>(key, false);
    }


    df::MSG::MSG(key_t key_, bool create) : key(key_) {
        if (create) {
            DF_CHECK_WITH_EXIT(!((msg_id = msgget(key, 0666 | IPC_CREAT | IPC_EXCL)) < 0),
                               fmt::format("Create MSG Wrong, key={}: {}", key, strerror(errno)));
        } else {
            DF_CHECK_WITH_EXIT(!((msg_id = msgget(key, 0)) < 0),
                               fmt::format("Get MSG Wrong, key={}: {}", key, strerror(errno)));
        }
    }

    void MSG::destroy() const {
        DF_CHECK_WITH_EXIT(msgctl(msg_id, IPC_RMID, nullptr) != -1,
                           fmt::format("Delete MSG Stat Wrong: {}", strerror(errno)));
    }

    std::string MSG::receive() const {
        msg_buffer buffer{};
        DF_CHECK_WITH_EXIT(msgrcv(msg_id, &buffer, sizeof(buffer.msg_text), 1, 0) != -1,
                           fmt::format("Receive MSG Wrong: {}", strerror(errno)));
        return buffer.msg_text;
    }

    void MSG::send(const std::string &msg) const {
        msg_buffer buffer{};
        buffer.msg_type = 1;
        strcpy(buffer.msg_text, msg.c_str());
        DF_CHECK_WITH_EXIT(msgsnd(msg_id, &buffer, sizeof(buffer.msg_text), 0) != -1,
                           fmt::format("Send MSG Wrong: {}", strerror(errno)));
    }
}