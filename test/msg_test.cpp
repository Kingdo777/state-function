//
// Created by kingdo on 23-12-22.
//
#include <df/msg/msg.h>
#include <iostream>

struct msg_buffer {
    long msg_type;
    char msg_text[1024];
};

int main() {
    msg_buffer buffer{};
    auto msgid = msgget(0x00022222, 0666 | IPC_CREAT);
    DF_CHECK_WITH_EXIT(msgrcv(msgid, &buffer, sizeof(buffer.msg_text), 0, 0) != -1,
                       fmt::format("Receive MSG Wrong: {}", strerror(errno)));
    printf("type:%ld, text:%s\n", buffer.msg_type, buffer.msg_text);
    return 0;
}