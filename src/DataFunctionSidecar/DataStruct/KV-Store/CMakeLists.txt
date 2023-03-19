# 获取源文件
file(GLOB SOURCES_FILE */*.cpp *.cpp *.cc *.c)
file(GLOB HEADERS_FILE ${DataFunction_INCLUDE_DIR}/df/data-struct/kvstore/*.h)
# 生成库文件, 注意, 如果自定义各个lib之间存在引用关系, 需要手动添加
add_library(datafunction-struct-kvstore STATIC ${SOURCES_FILE} ${HEADERS_FILE})
# 在这里如果不用PUBLIC, 那么使用这些库的可执行程序, 将无法引用第三方库的头文件. 因为我们自己的库的头文件中会引用这些头文件,
# 这样当其他可执行程序如果引用了我们的自己的库的头文件, 就会提示找不到第三方库的头文件
target_link_libraries(datafunction-struct-kvstore PRIVATE df::common_dependencies df::utils df::shm df::smalloc)
target_include_directories(datafunction-struct-kvstore PRIVATE ${DataFunctionSidecar_INCLUDE_DIR})

# Ensure library generates readable stack traces
target_compile_options(datafunction-struct-kvstore PUBLIC -fno-omit-frame-pointer)
target_link_options(datafunction-struct-kvstore PUBLIC -Wl,--export-dynamic)

add_library(df::datafunction-struct-kvstore ALIAS datafunction-struct-kvstore)