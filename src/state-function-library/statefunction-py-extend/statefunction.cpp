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
#include <kvstore/StateFunctionKVStoreBucket.h>

static PyObject *StateFunctionError;

enum KWLIST {
    BUCKET_NAME,
    BUCKET_SIZE,
    USE_PIPE,
    ACTION_PIPE_KEY,
};
static std::string kwlist_string[] = {
        "bucket_name",
        "bucket_size",
        "use_pipe",
        "action_pipe_key",
};

static PyObject *
statefunction_create_bucket(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *bucket_name_data;
    size_t bucket_name_len;

    size_t bucket_size;

    bool use_pipe = false;
    key_t action_pipe_key = -1;

    static char *kwlist[] = {kwlist_string[KWLIST::BUCKET_NAME].data(),
                             kwlist_string[KWLIST::BUCKET_SIZE].data(),
                             kwlist_string[KWLIST::USE_PIPE].data(),
                             kwlist_string[KWLIST::ACTION_PIPE_KEY].data(),
                             nullptr};
    /// 解析参数这里有一个必须谨慎的地方, format必须和后面的数据类型一一对应, 否则会出现内存错误
    /// 例如: `k` 表示unsigned long, 和size_t对应, `i` 表示int, 和key_t对应
    /// 但是如果将`k`和key_t对应, 那么就会导致内存溢出, 因为key_t是int类型, 而`k`是unsigned long类型, 两者的内存大小不一致
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#k|pi", kwlist, &bucket_name_data, &bucket_name_len, &bucket_size,
                                     &use_pipe, &action_pipe_key))
        return nullptr;

    std::string bucket_name{bucket_name_data, bucket_name_len};

    if (bucket_name.empty()) {
        SPDLOG_INFO("bucket_name: {}, bucket_size: {}, use_pipe: {}, action_pipe_key: {}", bucket_name, bucket_size,
                    use_pipe, action_pipe_key);
        PyErr_SetString(StateFunctionError, "bucket_name is empty string");
        return nullptr;
    }


    if (bucket_name.empty()) {
        PyErr_SetString(StateFunctionError, "bucket_name is empty string");
        return nullptr;
    }

    auto type = &Bucket_Type;
    auto bucket = (Bucket *) (type->tp_alloc(type, 0));

    bucket->name = bucket_name;
    bucket->size = bucket_size;
    try {
        bucket->bucket = df::dataStruct::KV_Store::StateFunctionKVStoreBucket::CreateBucket(bucket_name,
                                                                                            bucket_size, use_pipe,
                                                                                            action_pipe_key);
    } catch (std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }

    // 这里不需要增加引用计数，是因为tp_alloc中已经增加了，
    // 如果不是将其作为返回值，其实是应该减1，作为返回值又要加1，正好抵消
//    Py_INCREF(bucket);

    return (PyObject *) bucket;
}

static PyObject *
statefunction_get_bucket(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *bucket_name_data;
    size_t bucket_name_len;

    bool use_pipe = false;
    key_t action_pipe_key;

    static char *kwlist[] = {kwlist_string[KWLIST::BUCKET_NAME].data(),
                             kwlist_string[KWLIST::USE_PIPE].data(),
                             kwlist_string[KWLIST::ACTION_PIPE_KEY].data(),
                             nullptr};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|pi", kwlist, &bucket_name_data, &bucket_name_len, &use_pipe,
                                     &action_pipe_key))
        return nullptr;

    std::string bucket_name{bucket_name_data, bucket_name_len};

    if (bucket_name.empty()) {
        PyErr_SetString(StateFunctionError, "bucket_name is empty string");
        return nullptr;
    }

    auto type = &Bucket_Type;
    auto bucket = (Bucket *) (type->tp_alloc(type, 0));

    try {
        bucket->name = bucket_name;
        bucket->bucket = df::dataStruct::KV_Store::StateFunctionKVStoreBucket::GetBucket(bucket_name, use_pipe,
                                                                                         action_pipe_key);
        bucket->size = bucket->bucket->getBucketSize();
    } catch (std::exception &e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }

//    Py_INCREF(bucket);

    return (PyObject *) bucket;
}

static PyObject *
statefunction_system(PyObject *self, PyObject *args) {
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return nullptr;

    SPDLOG_INFO("{}", command);
    sts = system(command);

    if (sts < 0) {
        PyErr_SetString(StateFunctionError, "System command failed");
        return nullptr;
    }
    return PyLong_FromLong(sts);
}

static PyMethodDef StateFunctionMethods[] = {
        {"system",        statefunction_system,                                       METH_VARARGS,
                                      "Execute a shell command."},
        {"create_bucket", reinterpret_cast<PyCFunction>(statefunction_create_bucket), METH_VARARGS | METH_KEYWORDS,
                "Create new bucket."},
        {"get_bucket",    reinterpret_cast<PyCFunction>(statefunction_get_bucket),    METH_VARARGS | METH_KEYWORDS,
                "Get exist bucket."},
        {nullptr,         nullptr, 0, nullptr}        /* Sentinel */
};

static struct PyModuleDef StateFunctionModule = {
        PyModuleDef_HEAD_INIT,
        "statefunction",   /* name of module */
        nullptr, /* module documentation, may be nullptr */
        -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
        StateFunctionMethods
};

PyMODINIT_FUNC
PyInit_statefunction(void) {
    PyObject *m;

    df::utils::initLog();

    m = PyModule_Create(&StateFunctionModule);
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

    StateFunctionError = PyErr_NewException("statefunction.error", nullptr, nullptr);
    Py_XINCREF(StateFunctionError);
    if (PyModule_AddObject(m, "error", StateFunctionError) < 0) {
        Py_XDECREF(StateFunctionError);
        Py_CLEAR(StateFunctionError);
        Py_DECREF(m);
        return nullptr;
    }

    return m;
}
