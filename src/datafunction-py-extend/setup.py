from setuptools import setup, Extension

INCLUDE_DIRECTORY = "/home/kingdo/CLionProjects/DataFunction/include"
LIB_DIRECTORY = "/home/kingdo/CLionProjects/DataFunction/cmake-build-debug/out/lib"

module = Extension('datafunction',
                   include_dirs=[INCLUDE_DIRECTORY],
                   libraries=['utils', 'shm'],
                   library_dirs=[LIB_DIRECTORY],
                   sources=['datafunction.cpp'])

setup(name='datafunction',
      version='2.0.0',
      description='This is a datafunction package',
      author="Kingdo",
      ext_modules=[module])
