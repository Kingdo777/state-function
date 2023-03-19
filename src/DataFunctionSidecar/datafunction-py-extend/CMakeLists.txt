df_lib_share(datafunction-py-extend)
target_link_libraries(datafunction-py-extend PRIVATE df::utils df::shm df::smalloc df::datafunction-struct-kvstore)

target_include_directories(datafunction-py-extend PRIVATE ${DataFunctionSidecar_INCLUDE_DIR})

#依赖 public_func库执行，POST_BUILD表示生成这个库完毕之后，就会执行下面的cmd
add_custom_command(TARGET datafunction-py-extend POST_BUILD
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND python3.10 setup.py build  #执行python脚本
        )