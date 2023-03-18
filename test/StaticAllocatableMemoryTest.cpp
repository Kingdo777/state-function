//
// Created by kingdo on 23-3-13.
//

#include <df/utils/smalloc.h>

int main() {
    char data[4096];
    auto p = std::make_shared<df::utils::StaticAllocatableMemory>(data, 4096);
    std::string start(data, 4096);

    char *start_alloc = static_cast<char *>(p->malloc(4000));
    memset(start_alloc, 's', 4000);
    p->free(start_alloc);


    char *a1 = static_cast<char *>(p->malloc(24));
    memset(a1, '1', 8);
    char *a2 = static_cast<char *>(p->malloc(8));
    memset(a2, '2', 8);
    char *a3 = static_cast<char *>(p->malloc(8));
    memset(a3, '3', 8);


    p->free(a3);
    p->free(a1);
    char *a4 = static_cast<char *>(p->malloc(8));
    memset(a1, '4', 7);
    p->free(a4);
    p->free(a2);

//    return 0;


    char *s1 = static_cast<char *>(p->malloc(8));
    memset(s1, '1', 8);
    p->free(s1);

    char *s2 = static_cast<char *>(p->malloc(100));
    memset(s2, '2', 100);
    char *s3 = static_cast<char *>(p->malloc(1000));
    memset(s3, '3', 1000);
    char *s4 = static_cast<char *>(p->malloc(88));
    memset(s4, '4', 88);
    p->free(s2);
    p->free(s3);
    char *s5 = static_cast<char *>(p->malloc(2500));
    memset(s5, '5', 2500);
    p->free(s4);
    char *s6 = static_cast<char *>(p->malloc(99));
    memset(s6, '6', 99);
    char *s7 = static_cast<char *>(p->malloc(99));
    memset(s7, '7', 99);
    char *s8 = static_cast<char *>(p->malloc(199));
    memset(s8, '8', 199);
    char *s9 = static_cast<char *>(p->malloc(399));
    memset(s9, '9', 399);
    p->free(s7);
    p->free(s8);
    p->free(s6);
    p->free(s5);
    p->free(s9);

    char *end_alloc = static_cast<char *>(p->malloc(4000));
    memset(end_alloc, 'e', 4000);
    p->free(end_alloc);

    std::string end(data, 4096);
    if (start == end)
        SPDLOG_INFO("GOOD");
}