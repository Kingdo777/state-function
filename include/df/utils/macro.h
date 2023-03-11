#pragma once

#include <climits> // for PIPE_BUF
#include <df/utils/log.h>


// We're always on x86_64

#ifndef DataFunction_FILE_CREAT_MODE
#define DataFunction_FILE_CREAT_MODE 0664
#endif

#ifndef DataFunction_DIR_CREAT_MODE
#define DataFunction_DIR_CREAT_MODE 0775
#endif


#define WK_CHECK_WITH_EXIT(condition, msg) \
    do                                     \
    {                                      \
        bool check = (condition);          \
        if (check)                         \
            break;                         \
        WK_CHECK(check, msg);              \
        exit(EXIT_FAILURE);                \
    } while (false)

#define WK_CHECK(condition, msg) \
    do                           \
    {                            \
        if (!(condition))        \
            SPDLOG_ERROR((msg)); \
    } while (false)

