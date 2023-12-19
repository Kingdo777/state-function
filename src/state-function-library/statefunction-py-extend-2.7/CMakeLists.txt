pkg_check_modules(python-2.7 REQUIRED python-2.7)

df_lib_share(python-extend-statefunction-2.7)
target_link_libraries(python-extend-statefunction-2.7 PRIVATE df::utils df::shm df::smalloc python2.7)

target_include_directories(python-extend-statefunction-2.7 PRIVATE ${StateFunctionSidecar_INCLUDE_DIR} ${python-2.7_INCLUDE_DIRS})

#依赖 public_func库执行，POST_BUILD表示生成这个库完毕之后，就会执行下面的cmd
add_custom_command(TARGET python-extend-statefunction-2.7 POST_BUILD
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMAND python2.7 setup.py build bdist_wheel #执行python脚本
        )