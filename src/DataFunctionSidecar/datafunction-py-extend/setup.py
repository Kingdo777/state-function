from setuptools import setup, Extension

INCLUDE_DIRECTORY = "/home/kingdo/CLionProjects/DataFunction/include"
DataFunctionSidecar_INCLUDE = "/home/kingdo/CLionProjects/DataFunction/src/DataFunctionSidecar/include"
LIB_DIRECTORY = "/home/kingdo/CLionProjects/DataFunction/cmake-build-debug/out/lib"

module = Extension('datafunction',
                   include_dirs=[INCLUDE_DIRECTORY, DataFunctionSidecar_INCLUDE],
                   libraries=['utils', 'shm', 'smalloc', 'datafunction-struct-kvstore'],
                   library_dirs=[LIB_DIRECTORY],
                   extra_compile_args=['-std=c++20'],
                   sources=['datafunction.cpp'])

setup(name='datafunction',
      version='3.0.0',
      description='This is a datafunction package',
      author="Kingdo",
      ext_modules=[module])
