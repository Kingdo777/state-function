add_executable(Test-StaticAllocatableMemory StaticAllocatableMemoryTest.cpp)
target_include_directories(Test-StaticAllocatableMemory PRIVATE ${DataFunction_INCLUDE_DIR})
target_link_libraries(Test-StaticAllocatableMemory df::utils)


add_executable(Test-DataFunctionKVStoreBucket DataFunctionKVStoreBucketTest.cpp)
target_include_directories(Test-DataFunctionKVStoreBucket PRIVATE ${DataFunction_INCLUDE_DIR})
target_link_libraries(Test-DataFunctionKVStoreBucket df::utils df::datafunction-struct-kvstore)

add_executable(Test-Cpp cppTest.cpp)
target_include_directories(Test-Cpp PRIVATE ${DataFunction_INCLUDE_DIR})
target_link_libraries(Test-Cpp df::utils)

