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
#include <df/utils/log.h>
#include <df/shm/shm.h>

extern "C" {
static PyObject *DataFunctionError;

static PyObject *
datafunction_read(PyObject *self, PyObject *args) {
    char content[10];

    if (!PyArg_ParseTuple(args, ""))
        return nullptr;

    read_ipc(content, 10);

    return Py_BuildValue("s", content);
}

static PyObject *
datafunction_write(PyObject *self, PyObject *args) {
    const char *content;

    if (!PyArg_ParseTuple(args, "s", &content))
        return nullptr;

    write_ipc(std::string{content, 10});

    return Py_BuildValue("");
}

static PyObject *
datafunction_write_byte(PyObject *self, PyObject *args) {
    const char *content;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "s#", &content, &length))
        return nullptr;

    SPDLOG_INFO("content:{}, len:{}", content, length);

    write_ipc(std::string{content, 10});

    return Py_BuildValue("");
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
        {"system", datafunction_system, METH_VARARGS,
                               "Execute a shell command."},
        {"read", datafunction_read, METH_VARARGS,
                               "DataFunction read."},
        {"write", datafunction_write, METH_VARARGS,
                               "DataFunction write."},
        {"write_bytes", datafunction_write_byte, METH_VARARGS,
                               "DataFunction write_bytes."},
        {nullptr,  nullptr, 0, nullptr}        /* Sentinel */
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
};
