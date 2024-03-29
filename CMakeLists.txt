cmake_minimum_required(VERSION 3.16)
project(StateFunction)

# 给编译输出的结果, 添加颜色高亮效果 (https://zhuanlan.zhihu.com/p/368359203)
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    add_compile_options(-fdiagnostics-color=always)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    add_compile_options(-fcolor-diagnostics)
endif ()

# -Wall 显示所有警告信息(https://blog.csdn.net/cjtstrive/article/details/85375477)
# -fPIC 作用于编译阶段，告诉编译器产生与位置无关代码(Position-Independent Code)（http://blog.sina.com.cn/s/blog_54f82cc201011op1.html）
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -Wall")
# -g 生成操作系统原生格式(stabs, COFF, XCOFF, or DWARF)的调试信息，gdb可以使用这些调试信息(http://walkerdu.com/2020/04/22/gcc_optimization/)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g")
set(CMAKE_CXX_STANDARD 20)

option(ENABLE_TRACE "Statistics execution time" ON)

# 设置自定义的include目录
set(StateFunction_INCLUDE_DIR ${CMAKE_CURRENT_LIST_DIR}/include)

# 设置bin，lib的输出目录
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/out/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/out/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/out/bin)

# 引入第三方的module
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake;${CMAKE_MODULE_PATH}")
include(ExternalProjects)

if (${ENABLE_TRACE})
    add_definitions(-DENABLE_TRACE)
endif ()

function(df_lib_share lib_name)
    # 获取源文件
    file(GLOB SOURCES_FILE */*.cpp *.cpp *.cc *.c)
    file(GLOB HEADERS_FILE ${StateFunction_INCLUDE_DIR}/df/${lib_name}/*.h)
    # 生成库文件, 注意, 如果自定义各个lib之间存在引用关系, 需要手动添加
    add_library(${lib_name} SHARED ${SOURCES_FILE} ${HEADERS_FILE})
    # 在这里如果不用PUBLIC, 那么使用这些库的可执行程序, 将无法引用第三方库的头文件. 因为我们自己的库的头文件中会引用这些头文件,
    # 这样当其他可执行程序如果引用了我们的自己的库的头文件, 就会提示找不到第三方库的头文件
    target_link_libraries(${lib_name} PRIVATE df::common_dependencies)
    add_library(df::${lib_name} ALIAS ${lib_name})

    # Ensure library generates readable stack traces
    target_compile_options(${lib_name} PUBLIC -fno-omit-frame-pointer)
    target_link_options(${lib_name} PUBLIC -Wl,--export-dynamic)
endfunction()

function(df_lib_static lib_name)
    # 获取源文件
    file(GLOB SOURCES_FILE */*.cpp *.cpp *.cc *.c)
    file(GLOB HEADERS_FILE ${StateFunction_INCLUDE_DIR}/df/${lib_name}/*.h)
    # 生成库文件, 注意, 如果自定义各个lib之间存在引用关系, 需要手动添加
    add_library(${lib_name} STATIC ${SOURCES_FILE} ${HEADERS_FILE})
    # 在这里如果不用PUBLIC, 那么使用这些库的可执行程序, 将无法引用第三方库的头文件. 因为我们自己的库的头文件中会引用这些头文件,
    # 这样当其他可执行程序如果引用了我们的自己的库的头文件, 就会提示找不到第三方库的头文件
    target_link_libraries(${lib_name} PRIVATE df::common_dependencies)
    add_library(df::${lib_name} ALIAS ${lib_name})

    # Ensure library generates readable stack traces
    target_compile_options(${lib_name} PUBLIC -fno-omit-frame-pointer)
    target_link_options(${lib_name} PUBLIC -Wl,--export-dynamic)
endfunction()

add_subdirectory(src/common)
add_subdirectory(src/state-function-action)
add_subdirectory(src/state-function-library)

add_subdirectory(test)

