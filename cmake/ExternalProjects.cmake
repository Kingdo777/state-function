include(FindGit)
find_package(Git REQUIRED)
include(FetchContent)
find_package(Threads REQUIRED)

#------------- 将所有的第三方包, 全部打包成一个依赖库 ------------------------
# 创建一个INTERFACE库，一个INTERFACE库不会直接创建编译目标文件, 与下面的INTERFACE并不是同一概念
add_library(common_dependencies INTERFACE)

#----------------------- RapidJSON ------------------------------------
# cmake -DRAPIDJSON_BUILD_DOC=false -DRAPIDJSON_BUILD_EXAMPLES=false -DRAPIDJSON_BUILD_TESTS=false ..
find_package(RapidJSON QUIET)
if (NOT RapidJSON_FOUND)
    message("RapidJSON not found. Downloading it from source...")
    FetchContent_Declare(
            RapidJSON
            GIT_REPOSITORY https://github.com/Tencent/rapidjson.git
            GIT_TAG v1.1.0
            GIT_SHALLOW true
    )
    set(RAPIDJSON_BUILD_DOC OFF CACHE BOOL "")
    set(RAPIDJSON_BUILD_EXAMPLES OFF CACHE BOOL "")
    set(RAPIDJSON_BUILD_TESTS OFF CACHE BOOL "")
    FetchContent_MakeAvailable(RapidJSON)
    target_include_directories(common_dependencies INTERFACE ${rapidjson_SOURCE_DIR}/include)
else ()
    target_include_directories(common_dependencies INTERFACE ${RAPIDJSON_INCLUDE_DIRS})
endif ()

#----------------------- SpdLog ------------------------------------
#cmake -DSPDLOG_BUILD_ALL=false -DSPDLOG_BUILD_SHARED=false -DSPDLOG_ENABLE_PCH=false -DSPDLOG_BUILD_EXAMPLE_HO=false -DSPDLOG_BUILD_TESTS_HO=false -DSPDLOG_BUILD_BENCH=false -DSPDLOG_SANITIZE_ADDRESS=false -DSPDLOG_BUILD_WARNINGS=false ..
find_package(spdlog QUIET)
if (NOT spdlog_FOUND)
    message("SpdLog not found. Downloading it from source...")
    FetchContent_Declare(
            spdlog
            GIT_REPOSITORY https://github.com/gabime/spdlog.git
            GIT_TAG v1.9.2
            GIT_SHALLOW true
    )
    set(SPDLOG_BUILD_ALL OFF CACHE BOOL "")
    set(SPDLOG_BUILD_SHARED OFF CACHE BOOL "")
    set(SPDLOG_ENABLE_PCH OFF CACHE BOOL "")
    set(SPDLOG_BUILD_EXAMPLE_HO OFF CACHE BOOL "")
    set(SPDLOG_BUILD_TESTS_HO OFF CACHE BOOL "")
    set(SPDLOG_BUILD_BENCH OFF CACHE BOOL "")
    set(SPDLOG_SANITIZE_ADDRESS OFF CACHE BOOL "")
    set(SPDLOG_BUILD_WARNINGS OFF CACHE BOOL "")

    FetchContent_MakeAvailable(spdlog)
endif ()
# INTERFACE 表示, df::common_dependencies本身不会链接后面一系列的库及其头文件,
# 而链接df::common_dependencies的库或者可执行程序会链接这些库及其头文件,
# INTERFACE与PRIVATE的效果刚好相反. 而PUBLIC则是两者都会链接库及其头文件.
# 详见https://blog.csdn.net/weixin_43862847/article/details/119762230
target_link_libraries(common_dependencies INTERFACE spdlog)

#----------------------- fmt ------------------------------------
find_package(fmt QUIET)
if (NOT fmt_FOUND)
    message("fmt not found.  Downloading it from source...")
    FetchContent_Declare(
            fmt
            GIT_REPOSITORY https://github.com/fmtlib/fmt.git
            GIT_TAG 8.1.1
            GIT_SHALLOW true
    )

    FetchContent_MakeAvailable(fmt)
endif ()
target_link_libraries(common_dependencies INTERFACE fmt)

#----------------------- pistache ------------------------------------
# ./install
find_package(PkgConfig REQUIRED)
set(ENV{PKG_CONFIG_PATH}
        /usr/local/lib64/pkgconfig:$ENV{PKG_CONFIG_PATH})
pkg_check_modules(Pistache QUIET IMPORTED_TARGET libpistache)
if (NOT Pistache_FOUND)
    message("pistache not found.  Downloading it from source...")
    FetchContent_Declare(
            pistache
            GIT_REPOSITORY https://github.com/Kingdo777/pistache
            GIT_SHALLOW true
    )
    set(PISTACHE_BUILD_TESTS OFF CACHE BOOL "")
    set(PISTACHE_BUILD_FUZZ OFF CACHE BOOL "")
    set(PISTACHE_BUILD_EXAMPLES OFF CACHE BOOL "")
    set(DPISTACHE_BUILD_DOCS OFF CACHE BOOL "")

    FetchContent_MakeAvailable(pistache)
    target_link_libraries(common_dependencies INTERFACE pistache_shared)
else ()
    target_link_libraries(common_dependencies INTERFACE PkgConfig::Pistache)
endif ()

#----------------------- CURL ------------------------------------
#sudo apt-get install libcurl4-openssl-dev
find_package(CURL REQUIRED)
target_link_libraries(common_dependencies INTERFACE CURL::libcurl)

#----------------------- Boost ------------------------------------
# sudo apt-get install libboost-filesystem-dev
# 因为boost太大了，不适合使用FetchContent进行安装
find_package(Boost COMPONENTS filesystem REQUIRED)
target_link_libraries(common_dependencies INTERFACE Boost::filesystem)

#----------------------- CPython ------------------------------------
# sudo apt-get install python3.10-dev
# pkg-config --list-all | grep python
pkg_check_modules(python-3.10 REQUIRED python-3.10)
target_link_libraries(common_dependencies INTERFACE python3.10)
message(STATUS ${python-3.10_INCLUDE_DIRS})
target_include_directories(common_dependencies INTERFACE ${python-3.10_INCLUDE_DIRS})

#---------------------------其他库-------------------------------------
target_link_libraries(common_dependencies INTERFACE
        pthread
        dl
        util
        )
#--------------------------------------------------------------------

target_include_directories(common_dependencies INTERFACE ${DataFunction_INCLUDE_DIR})

# 起一个别名, 因为当前CMAKE不支持直接生成df::格式的lib
add_library(df::common_dependencies ALIAS common_dependencies)