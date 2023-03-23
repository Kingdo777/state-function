df_lib_share(python-extend-datafunction)
target_link_libraries(python-extend-datafunction PRIVATE df::utils df::shm df::smalloc df::datafunction-struct-kvstore)

target_include_directories(python-extend-datafunction PRIVATE ${DataFunctionSidecar_INCLUDE_DIR})

#依赖 public_func库执行，POST_BUILD表示生成这个库完毕之后，就会执行下面的cmd
add_custom_command(TARGET python-extend-datafunction POST_BUILD
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND python3.10 setup.py build  #执行python脚本
        )