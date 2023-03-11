//
// Created by kingdo on 2022/3/16.
//

#ifndef DataFunction_DL_H
#define DataFunction_DL_H

#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <fstream>
#include <iostream>
#include <string>
#include <df/utils/radom.h>

namespace df::utils
{

    /// 以下代码，参考自libuv的`src/unix/dl.c`

    char* df_strdup(const char* s);

    void df_free(void* ptr);

    class Lib
    {
    public:
        Lib() = default;

        int open(const std::string& code);

        int open(const char* filename);

        void close();

        int sym(const char* name, void** ptr);

        [[nodiscard]] const char* errors() const;

        int error();

        void* handle = nullptr;

        char* errmsg = nullptr;
    };

}

#endif //DataFunction_DL_H
