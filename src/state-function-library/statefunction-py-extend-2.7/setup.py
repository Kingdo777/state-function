from setuptools import setup, Extension

INCLUDE_DIRECTORY = "../../../include"
StateFunctionSidecar_INCLUDE = "../include"
LIB_DIRECTORY = "../../../cmake-build-debug/out/lib"

module = Extension('statefunction',
                   include_dirs=[INCLUDE_DIRECTORY, StateFunctionSidecar_INCLUDE],
                   libraries=['utils', 'shm', 'smalloc', "curl"],
                   library_dirs=[LIB_DIRECTORY],
                   extra_compile_args=['-std=c++20'],
                   sources=['statefunction.cpp'])

setup(name='statefunction',
      version='2.0.0',
      description='This is a statefunction package',
      author="Kingdo",
      ext_modules=[module])
