pkg_check_modules(python-3.10 REQUIRED python-3.10)

df_lib_share(python-extend-statefunction)
target_link_libraries(python-extend-statefunction PRIVATE df::utils df::shm df::msg df::smalloc python3.10)

target_include_directories(python-extend-statefunction PRIVATE ${StateFunctionSidecar_INCLUDE_DIR}  ${python-3.10_INCLUDE_DIRS})


#依赖 public_func库执行，POST_BUILD表示生成这个库完毕之后，就会执行下面的cmd
add_custom_command(TARGET python-extend-statefunction POST_BUILD
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND python3.10 setup.py build bdist_wheel  #执行python脚本
        )