#include <df/utils/log.h>
#include <df/utils/timing.h>
#include <df/shm/shm.h>
#include "src/datafunction-py-interface/datafunction-py-interface.h"

int main() {
    df::utils::initLog("Main");
    TIMING_START(log)

//    write_ipc("Kingdo");
//    read_ipc();

    char buf[10] = {"Kingdo"};
    write_ipc_py(buf, 10);

    std::string out;
    out.reserve(10);
    read_ipc_py(out.data(), 10);
    SPDLOG_INFO("{}", out);

    TIMING_END(log)
}