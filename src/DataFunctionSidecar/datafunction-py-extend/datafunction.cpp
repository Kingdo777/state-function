//
// Created by kingdo on 23-3-7.
//


/// C/C++扩展Python文档:(https://docs.python.org/zh-cn/3.10/c-api/)
/// 1. 概述 (https://docs.python.org/zh-cn/3.10/c-api/intro.html)
/// 2. 解析参数并构建值变量 (https://docs.python.org/zh-cn/3.10/c-api/arg.html#)
/// 3. 引用计数 (https://docs.python.org/zh-cn/3.10/c-api/refcounting.html#reference-counting)

/// 使用 C 或 C++ 扩展 Python (https://docs.python.org/zh-cn/3.10/extending/extending.html#extending-python-with-c-or-c)

/// 优秀博客
/// 1.参数解析与结果封装 https://www.cnblogs.com/jianmu/p/7367566.html
/// 2.引用计数问题的处理 https://www.cnblogs.com/jianmu/p/7367698.html
/// 1.异常和错误处理 https://www.cnblogs.com/jianmu/p/7469146.html


#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "kvBucket.h"
#include <df/utils/log.h>
#include <kvstore/DataFunctionKVStoreBucket.h>

static PyObject *DataFunctionError;

static PyObject *
datafunction_create_bucket(PyObject *self, PyObject *args) {
    const char *bucket_name_data;
    size_t bucket_name_len;

    size_t bucket_size;

    if (!PyArg_ParseTuple(args, "s#K", &bucket_name_data, &bucket_name_len, &bucket_size))
        return nullptr;

    std::string bucket_name{bucket_name_data, bucket_name_len};

    if (bucket_name.empty()) {
        PyErr_SetString(DataFunctionError, "bucket_name is empty string");
        return nullptr;
    }

    auto type = &Bucket_Type;
    auto bucket = (Bucket *) (type->tp_alloc(type, 0));

    bucket->name = bucket_name;
    bucket->size = bucket_size;
    bucket->bucket = std::make_shared<df::dataStruct::KV_Store::DataFunctionKVStoreBucket>(bucket_name, bucket_size);

    // 这里不需要增加引用计数，是因为tp_alloc中已经增加了，
    // 如果不是将其作为返回值，其实是应该减1，作为返回值又要加1，正好抵消
//    Py_INCREF(bucket);

    return (PyObject *) bucket;
}

static PyObject *
datafunction_get_bucket(PyObject *self, PyObject *args) {
    const char *bucket_name_data;
    size_t bucket_name_len;


    if (!PyArg_ParseTuple(args, "s#", &bucket_name_data, &bucket_name_len))
        return nullptr;

    std::string bucket_name{bucket_name_data, bucket_name_len};

    if (bucket_name.empty()) {
        PyErr_SetString(DataFunctionError, "bucket_name is empty string");
        return nullptr;
    }

    auto type = &Bucket_Type;
    auto bucket = (Bucket *) (type->tp_alloc(type, 0));

    bucket->name = bucket_name;
    bucket->bucket = std::make_shared<df::dataStruct::KV_Store::DataFunctionKVStoreBucket>(bucket_name);
    bucket->size = bucket->bucket->getBucketSize();

//    Py_INCREF(bucket);

    return (PyObject *) bucket;
}

static PyObject *
datafunction_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return nullptr;

    SPDLOG_INFO("{}", command);
    sts = system(command);

    if (sts < 0) {
        PyErr_SetString(DataFunctionError, "System command failed");
        return nullptr;
    }
    return PyLong_FromLong(sts);
}

static PyMethodDef DataFunctionMethods[] = {
        {"system",        datafunction_system,        METH_VARARGS,
                                      "Execute a shell command."},
        {"create_bucket", datafunction_create_bucket, METH_VARARGS,
                                      "Create new bucket."},
        {"get_bucket",    datafunction_get_bucket,    METH_VARARGS,
                                      "Get exist bucket."},
        {nullptr,         nullptr, 0, nullptr}        /* Sentinel */
};

static struct PyModuleDef DataFunctionModule = {
        PyModuleDef_HEAD_INIT,
        "datafunction",   /* name of module */
        nullptr, /* module documentation, may be nullptr */
        -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
        DataFunctionMethods
};

PyMODINIT_FUNC
PyInit_datafunction(void) {
    PyObject *m;

    m = PyModule_Create(&DataFunctionModule);
    if (m == nullptr)
        return nullptr;

    if (PyType_Ready(&Bucket_Type) < 0)
        return nullptr;
    Py_INCREF(&Bucket_Type);
    if (PyModule_AddObject(m, "Bucket", (PyObject *) &Bucket_Type) < 0) {
        Py_DECREF(&Bucket_Type);
        Py_DECREF(m);
        return nullptr;
    }

    DataFunctionError = PyErr_NewException("datafunction.error", nullptr, nullptr);
    Py_XINCREF(DataFunctionError);
    if (PyModule_AddObject(m, "error", DataFunctionError) < 0) {
        Py_XDECREF(DataFunctionError);
        Py_CLEAR(DataFunctionError);
        Py_DECREF(m);
        return nullptr;
    }

    return m;
}
