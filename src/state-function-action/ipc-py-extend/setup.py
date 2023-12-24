from setuptools import setup, Extension

INCLUDE_DIRECTORY = "../../../include"
LIB_DIRECTORY = "../../../cmake-build-debug/out/lib"

module = Extension('ipc',
                   include_dirs=[INCLUDE_DIRECTORY],
                   libraries=['utils', 'shm', 'msg'],
                   library_dirs=[LIB_DIRECTORY],
                   extra_compile_args=['-std=c++20'],
                   sources=['ipc.cpp'])

setup(name='ipc',
      version='1.0.0',
      description='This is a ipc package',
      author="Kingdo",
      ext_modules=[module])
