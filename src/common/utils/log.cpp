//
// Created by 14408 on 2022/2/18.
//
#include <df/utils/log.h>
#include <df/utils/config.h>
#include <filesystem>

std::string getExecName() {
    auto currentTime = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::microseconds>(currentTime.time_since_epoch());
    auto microsecond = timestamp.count() % 1000000;

    char buffer[1024];
    auto size = readlink("/proc/self/exe", buffer, sizeof(buffer) - 1);
    auto exec_name = std::filesystem::path(std::string(buffer, size)).filename().string();

    return fmt::format("{}-{}", exec_name, microsecond);
}

void df::utils::initLog(std::string exec_name) {

    bool enable_file = Config::EnableLogFile() == "on";

    if (enable_file) {
        if (exec_name.empty()) {
            exec_name = getExecName();
        }
        auto path = std::filesystem::path(Config::LogFileBaseDir()).append(exec_name).append("log");
        if (!std::filesystem::exists(path)) {
            std::filesystem::create_directories(path.parent_path());
            creat(path.c_str(), 0600);
        }
        spdlog::set_default_logger(spdlog::basic_logger_mt("new_default_logger", path.c_str()));
    }

    // Docs: https://github.com/gabime/spdlog/wiki/3.-Custom-formatting
    // %^ %$    之间的内容将会被标上颜色
    // %H:%M:%S 是时间格式
    // [%t]     是线程ID
    // %=6l     是全写log类型，info、debug等，=6表示占6字符居中
    // %-60v    是log内容，-60表示占60字符左对齐
    // %@       是文件名和行号
    // spdlog::set_pattern(fmt::format("%^ [%H:%M:%S] [%t] [%=6l]%$ %-60v [%@]");

    spdlog::level::level_enum log_level = Config::LogLevel();
    CHECK_MIN_LEVEL(log_level)
    spdlog::set_level(log_level);
    spdlog::flush_on(log_level);
}

void df::utils::printAllENV() {
    char **env = environ;
    while (*env != nullptr) {
        SPDLOG_INFO(*env);
        env++;
    }
}
