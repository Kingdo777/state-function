add_executable(Test-StaticAllocatableMemory StaticAllocatableMemoryTest.cpp)
target_include_directories(Test-StaticAllocatableMemory PRIVATE ${StateFunction_INCLUDE_DIR})
target_link_libraries(Test-StaticAllocatableMemory df::utils df::smalloc)

set(StateFunctionSidecar_INCLUDE_DIR ${CMAKE_SOURCE_DIR}/src/state-function-library/include)
add_executable(Test-StateFunctionKVStoreBucket StateFunctionKVStoreBucketTest.cpp)
target_include_directories(Test-StateFunctionKVStoreBucket PRIVATE ${StateFunction_INCLUDE_DIR})
target_include_directories(Test-StateFunctionKVStoreBucket PRIVATE ${StateFunctionSidecar_INCLUDE_DIR})
target_link_libraries(Test-StateFunctionKVStoreBucket df::utils df::shm df::smalloc)

add_executable(Test-Cpp cppTest.cpp)
target_include_directories(Test-Cpp PRIVATE ${StateFunction_INCLUDE_DIR})
target_link_libraries(Test-Cpp df::utils)

