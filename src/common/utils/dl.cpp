//
// Created by kingdo on 2022/3/16.
//

#include <fmt/format.h>
#include <sys/stat.h>
#include <df/utils/dl.h>

namespace df::utils
{

    int Lib::open(const std::string& code)
    {
        const std::string libDir = "/tmp/df";
        std::string filename     = fmt::format("{}/lib{}.so", libDir, randomString(15));
        system(fmt::format("mkdir -p {}", libDir).c_str());
        std::ofstream f;
        f.open(filename.c_str(), std::ios::out | std::ios::binary);
        f << code;
        f.flush();
        f.close();
        return this->open(filename.c_str());
    }

    int Lib::open(const char* filename)
    {
        dlerror(); /* Reset error status. */
        errmsg = nullptr;
        handle = dlopen(filename, RTLD_LAZY);
        return handle ? 0 : error();
    }

    void Lib::close()
    {
        df_free(errmsg);
        errmsg = nullptr;

        if (handle)
        {
            /* Ignore errors. No good way to  const constsignal them without leaking memory. */
            dlclose(handle);
            handle = nullptr;
        }
    }

    int Lib::sym(const char* name, void** ptr)
    {
        dlerror(); /* Reset error status. */
        *ptr = dlsym(handle, name);
        return error();
    }

    const char* Lib::errors() const
    {
        return errmsg ? errmsg : "no error";
    }

    int Lib::error()
    {
        const char* errmsg_;
        errmsg_ = dlerror();

        df_free(errmsg);

        if (errmsg_)
        {
            errmsg = df_strdup(errmsg_);
            return -1;
        }
        else
        {
            errmsg = nullptr;
            return 0;
        }
    }

    char* df_strdup(const char* s)
    {
        size_t len = strlen(s) + 1;
        char* m    = (char*)malloc(len);
        if (m == nullptr)
            return nullptr;
        return (char*)memcpy(m, s, len);
    }

    void df_free(void* ptr)
    {
        int saved_errno;

        /* Libuv expects that free() does not clobber errno.  The system allocator
         * honors that assumption but custom allocators may not be so careful.
         */
        saved_errno = errno;
        free(ptr);
        errno = saved_errno;
    }
}
